"""Client HTTP de l'API modele. (C10)

Point important pour la competence C10 : l'application **n'importe pas** le
moteur. Elle parle a l'API modele par HTTP, comme le ferait n'importe quel autre
consommateur. C'est ce qui rend le decouplage demontrable : on peut arreter
l'API et constater que l'application se degrade proprement au lieu de tomber.

Toutes les pannes previsibles sont converties en une exception unique porteuse
d'un message destine a l'utilisateur final, jamais d'une trace technique.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from concorde.common.config import get_settings
from concorde.common.logging_setup import request_id_var, setup_logging
from concorde.service.observabilite import ENTETE_CORRELATION

log = setup_logging("app")

DELAI_CONNEXION_S = 2.0
DELAI_LECTURE_S = 5.0


@dataclass(slots=True)
class ErreurService(Exception):
    """Panne de l'API modele, formulee pour l'utilisateur."""

    message_utilisateur: str
    detail_technique: str
    statut: int | None = None

    def __str__(self) -> str:  # pragma: no cover
        return self.detail_technique


class ClientModele:
    """Appelle l'API modele avec des delais bornes et une gestion d'erreur explicite."""

    def __init__(self, url_base: str | None = None, cle_api: str | None = None) -> None:
        reglages = get_settings()
        self.url_base = (url_base or reglages.model_api_url).rstrip("/")
        # L'application se presente avec sa propre cle : elle n'herite pas de
        # celle de l'utilisateur et ne peut pas en usurper les droits.
        self.cle_api = cle_api or next(
            (c for c, r in reglages.api_key_roles.items() if r == "analyst"),
            next(iter(reglages.api_key_roles), ""),
        )

    def _entetes(self) -> dict[str, str]:
        return {
            "X-API-Key": self.cle_api,
            ENTETE_CORRELATION: request_id_var.get(),
            "Accept": "application/json",
        }

    def _appeler(self, methode: str, chemin: str, **kwargs: Any) -> Any:
        url = f"{self.url_base}{chemin}"
        try:
            with httpx.Client(
                timeout=httpx.Timeout(DELAI_LECTURE_S, connect=DELAI_CONNEXION_S)
            ) as client:
                reponse = client.request(methode, url, headers=self._entetes(), **kwargs)
        except httpx.ConnectError as exc:
            log.error(f"API modele injoignable : {exc}",
                      extra={"event": "api_injoignable", "url": url})
            raise ErreurService(
                "Le service d'evaluation est momentanement indisponible. "
                "Aucun resultat ne peut etre affiche : plutot qu'une reponse approximative, "
                "l'application prefere ne rien avancer.",
                f"ConnectError sur {url}: {exc}",
            ) from exc
        except httpx.TimeoutException as exc:
            log.error(f"API modele hors delai : {exc}",
                      extra={"event": "api_timeout", "url": url})
            raise ErreurService(
                "Le service d'evaluation met trop de temps a repondre. Reessayez dans un instant.",
                f"Timeout sur {url}: {exc}",
            ) from exc

        if reponse.status_code == 422:
            detail = reponse.json().get("detail", [])
            champs = ", ".join(
                str(e.get("loc", ["?"])[-1]) for e in detail if isinstance(e, dict)
            )
            raise ErreurService(
                f"Les informations saisies ne sont pas valides ({champs}). Corrigez-les et "
                "relancez l'evaluation.",
                f"422 sur {url}: {detail}",
                statut=422,
            )
        if reponse.status_code == 503:
            raise ErreurService(
                "Le modele d'evaluation n'est pas charge sur le serveur. "
                "L'application ne peut pas produire de resultat.",
                f"503 sur {url}: {reponse.text[:200]}",
                statut=503,
            )
        if reponse.status_code >= 400:
            log.error(f"Reponse {reponse.status_code} de l'API modele",
                      extra={"event": "api_erreur", "statut": reponse.status_code, "url": url})
            raise ErreurService(
                "Le service d'evaluation a rencontre une erreur. L'incident est journalise.",
                f"{reponse.status_code} sur {url}: {reponse.text[:200]}",
                statut=reponse.status_code,
            )
        return reponse.json()

    def sante(self) -> dict[str, Any]:
        return self._appeler("GET", "/sante")

    def evaluer(self, rapprochement: dict[str, Any]) -> dict[str, Any]:
        return self._appeler("POST", "/predict", json=rapprochement)

    def fiche_modele(self) -> dict[str, Any]:
        return self._appeler("GET", "/modele/fiche")

    def regles(self) -> list[dict[str, str]]:
        return self._appeler("GET", "/regles")
