"""Observabilite des services : correlation, journal d'acces, metriques. (C11, C20)

Trois briques minimales mais reelles :

1. **Correlation** — chaque requete recoit (ou reprend) un `X-Request-ID`, place
   dans le contexte de journalisation. La meme valeur apparait dans le log de
   l'application, dans celui de l'API et dans celui du modele : un incident se
   reconstitue en filtrant sur un seul identifiant. (C21)
2. **Journal d'acces structure** — methode, chemin, statut, latence, role de
   l'appelant. Aucune donnee personnelle, aucune cle en clair.
3. **Metriques en memoire** — compteurs et latences par route, exposes en JSON
   sur `/metriques` et deverses sur disque pour le tableau de bord. Pas de
   Prometheus : la contrainte hors ligne interdit d'ajouter un service a
   installer, et un magasin en memoire suffit a demontrer seuils et alertes.
"""

from __future__ import annotations

import json
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from concorde.common.logging_setup import request_id_var, setup_logging

ENTETE_CORRELATION = "X-Request-ID"

#: Seuils de declenchement d'alerte, communs a toutes les routes.
SEUIL_LATENCE_P95_MS = 750.0
SEUIL_TAUX_ERREUR = 0.05


@dataclass(slots=True)
class StatistiquesRoute:
    appels: int = 0
    erreurs_client: int = 0
    erreurs_serveur: int = 0
    #: Fenetre glissante des dernieres latences, pour les percentiles.
    latences_ms: deque[float] = field(default_factory=lambda: deque(maxlen=512))

    def percentile(self, p: float) -> float:
        if not self.latences_ms:
            return 0.0
        ordonnees = sorted(self.latences_ms)
        rang = min(len(ordonnees) - 1, int(round(p * (len(ordonnees) - 1))))
        return round(ordonnees[rang], 2)

    @property
    def taux_erreur(self) -> float:
        return (self.erreurs_client + self.erreurs_serveur) / self.appels if self.appels else 0.0

    def en_dict(self) -> dict[str, Any]:
        return {
            "appels": self.appels,
            "erreurs_client": self.erreurs_client,
            "erreurs_serveur": self.erreurs_serveur,
            "taux_erreur": round(self.taux_erreur, 4),
            "latence_p50_ms": self.percentile(0.50),
            "latence_p95_ms": self.percentile(0.95),
            "latence_max_ms": round(max(self.latences_ms), 2) if self.latences_ms else 0.0,
        }


class Metriques:
    """Magasin de metriques en memoire, propre a un processus de service."""

    def __init__(self, service: str) -> None:
        self.service = service
        self.demarre_le = datetime.now(UTC).isoformat()
        self.routes: dict[str, StatistiquesRoute] = defaultdict(StatistiquesRoute)
        self.compteurs: dict[str, int] = defaultdict(int)

    def enregistrer(self, route: str, statut: int, latence_ms: float) -> None:
        stats = self.routes[route]
        stats.appels += 1
        stats.latences_ms.append(latence_ms)
        if 400 <= statut < 500:
            stats.erreurs_client += 1
        elif statut >= 500:
            stats.erreurs_serveur += 1

    def incrementer(self, nom: str, valeur: int = 1) -> None:
        self.compteurs[nom] += valeur

    def alertes(self) -> list[dict[str, Any]]:
        """Evalue les seuils et renvoie les alertes actives. (C11, C20)"""
        actives: list[dict[str, Any]] = []
        for route, stats in self.routes.items():
            if stats.appels < 5:
                continue  # trop peu d'appels pour conclure
            p95 = stats.percentile(0.95)
            if p95 > SEUIL_LATENCE_P95_MS:
                actives.append({
                    "severite": "avertissement", "regle": "latence_p95",
                    "route": route, "valeur": p95, "seuil": SEUIL_LATENCE_P95_MS,
                    "message": f"Latence p95 de {route} a {p95} ms "
                               f"(seuil {SEUIL_LATENCE_P95_MS} ms).",
                })
            if stats.taux_erreur > SEUIL_TAUX_ERREUR:
                actives.append({
                    "severite": "critique", "regle": "taux_erreur",
                    "route": route, "valeur": round(stats.taux_erreur, 4),
                    "seuil": SEUIL_TAUX_ERREUR,
                    "message": f"Taux d'erreur de {route} a {stats.taux_erreur:.1%} "
                               f"(seuil {SEUIL_TAUX_ERREUR:.0%}).",
                })
        return actives

    def instantane(self) -> dict[str, Any]:
        return {
            "service": self.service,
            "demarre_le": self.demarre_le,
            "horodatage": datetime.now(UTC).isoformat(),
            "routes": {r: s.en_dict() for r, s in self.routes.items()},
            "compteurs": dict(self.compteurs),
            "seuils": {
                "latence_p95_ms": SEUIL_LATENCE_P95_MS,
                "taux_erreur": SEUIL_TAUX_ERREUR,
            },
            "alertes": self.alertes(),
        }

    def deverser(self, chemin: Path) -> None:
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(
            json.dumps(self.instantane(), ensure_ascii=False, indent=2), encoding="utf-8"
        )


class ObservabiliteMiddleware(BaseHTTPMiddleware):
    """Correlation + journal d'acces + metriques, en une seule traversee."""

    def __init__(self, app, service: str, metriques: Metriques) -> None:
        super().__init__(app)
        self.service = service
        self.metriques = metriques
        self.log = setup_logging(service)

    async def dispatch(self, request: Request, call_next) -> Response:
        import uuid

        rid = request.headers.get(ENTETE_CORRELATION) or uuid.uuid4().hex
        jeton = request_id_var.set(rid)
        debut = time.perf_counter()
        statut = 500
        try:
            reponse = await call_next(request)
            statut = reponse.status_code
            reponse.headers[ENTETE_CORRELATION] = rid
            return reponse
        finally:
            latence = (time.perf_counter() - debut) * 1000
            route = request.scope.get("route")
            modele_route = getattr(route, "path", request.url.path)
            self.metriques.enregistrer(modele_route, statut, latence)
            self.log.info(
                f"{request.method} {modele_route} -> {statut} en {latence:.1f} ms",
                extra={
                    "event": "acces_http",
                    "methode": request.method,
                    "route": modele_route,
                    "statut": statut,
                    "latence_ms": round(latence, 2),
                    # Pseudonymise par le filtre RGPD avant ecriture.
                    "client_ip": request.client.host if request.client else "-",
                },
            )
            request_id_var.reset(jeton)
