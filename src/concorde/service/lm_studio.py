"""Adaptateur du service IA local LM Studio. (C7, C8)"""

from __future__ import annotations

import time
from typing import Any

import httpx

from concorde.common.config import get_settings
from concorde.common.logging_setup import setup_logging
from concorde.common.paths import MONITORING_MODEL
from concorde.service.observabilite import Metriques

SERVICE = "lm-studio"
EXPLICATION_TIMEOUT_SECONDES = 3.0
EXPLICATION_MAX_TOKENS = 90
EXPLICATION_MAX_CARACTERES = 1000
metriques = Metriques(SERVICE)
log = setup_logging(SERVICE)


class ServiceIADisponible(RuntimeError):
    """Leve lorsque LM Studio ou le modele retenu n'est pas disponible."""


def _consigne_de_redaction(verdict: dict[str, object]) -> str:
    """Transforme le verdict en consigne factuelle, sans le confier au LLM."""
    if verdict["statut"] == "non_evaluable":
        return (
            "Ecris une phrase de 20 mots maximum disant qu'aucun score n'est calcule "
            "car aucun diagnostic energetique n'a ete rapproche."
        )

    motifs = verdict.get("motifs", [])
    contradiction_majeure = any(
        isinstance(motif, dict) and motif.get("gravite") == "majeur" for motif in motifs
    )
    if contradiction_majeure:
        return (
            "Ecris une phrase de 20 mots maximum disant qu'une contradiction majeure "
            "a ete detectee et que des informations manquent."
        )

    niveau_anomalie = verdict["niveau_anomalie"]
    if niveau_anomalie == "atypique":
        return (
            "Ecris une phrase de 20 mots maximum disant que ce dossier s'ecarte des "
            "autres cas connus et merite une verification."
        )
    if niveau_anomalie == "a_verifier":
        return (
            "Ecris une phrase de 20 mots maximum disant que ce dossier merite une "
            "verification avant reutilisation."
        )

    confiance = verdict.get("confiance", {})
    niveau_confiance = confiance.get("niveau") if isinstance(confiance, dict) else None
    if niveau_confiance in {"faible", "insuffisant"}:
        return (
            "Ecris une phrase de 20 mots maximum disant que les informations sont trop "
            "fragiles pour une conclusion assuree."
        )
    if niveau_confiance == "moyen":
        return (
            "Ecris une phrase de 20 mots maximum disant que certaines informations "
            "manquent et que la lecture reste prudente."
        )
    return (
        "Ecris une phrase de 20 mots maximum disant qu'aucune contradiction connue "
        "n'a ete detectee dans les informations disponibles."
    )


class ClientLMStudio:
    """Client minimal de l'API OpenAI-compatible exposee par LM Studio."""

    def __init__(self, url_base: str | None = None, modele: str | None = None) -> None:
        reglages = get_settings()
        self.url_base = (url_base or reglages.lm_studio_url).rstrip("/")
        self.modele = modele or reglages.lm_studio_model

    def verifier_service(self) -> dict[str, Any]:
        debut = time.perf_counter()
        try:
            with httpx.Client(timeout=5.0) as client:
                reponse = client.get(f"{self.url_base}/models")
                reponse.raise_for_status()
            ids = [item.get("id") for item in reponse.json().get("data", [])]
        except httpx.HTTPError as exc:
            metriques.enregistrer("/v1/models", 503, (time.perf_counter() - debut) * 1000)
            raise ServiceIADisponible("LM Studio local est indisponible sur 127.0.0.1:1234") from exc

        disponible = self.modele in ids
        metriques.enregistrer("/v1/models", 200 if disponible else 503, (time.perf_counter() - debut) * 1000)
        if not disponible:
            raise ServiceIADisponible(f"Modele local attendu absent : {self.modele}; disponibles : {ids}")
        metriques.deverser(MONITORING_MODEL / "metriques_lm_studio.json")
        log.info("Service IA local verifie", extra={"event": "service_ia_verifie", "modele": self.modele})
        return {"disponible": True, "modele": self.modele, "modeles_exposes": ids}

    def reformuler_verdict(self, verdict: dict[str, object]) -> str:
        """Reformule une projection de verdict sans produire de nouvelle decision.

        Le contrat de la route appelante exclut les donnees brutes. Le client
        n'envoie pas le verdict : il convertit ses valeurs deja calculees en une
        consigne de redaction, que le LLM ne peut pas interpreter ni inverser.
        """
        debut = time.perf_counter()
        statut = 503
        metriques.incrementer("appels_reformulation")
        instruction = _consigne_de_redaction(verdict)
        try:
            with httpx.Client(timeout=EXPLICATION_TIMEOUT_SECONDES) as client:
                reponse = client.post(
                    f"{self.url_base}/chat/completions",
                    json={
                        "model": self.modele,
                        "temperature": 0,
                        "max_tokens": EXPLICATION_MAX_TOKENS,
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "Repond UNIQUEMENT par la phrase demandee, sans aucun "
                                    "raisonnement, sans preambule, sans guillemets."
                                ),
                            },
                            {"role": "user", "content": instruction},
                        ],
                    },
                )
                statut = reponse.status_code
                reponse.raise_for_status()
            choix = reponse.json()["choices"][0]
            contenu = choix["message"]["content"]
            raisonnement = choix.get("reasoning_content", "")
            tokens_raisonnement = reponse.json()["usage"]["completion_tokens_details"][
                "reasoning_tokens"
            ]
            if choix["finish_reason"] != "stop" or raisonnement or tokens_raisonnement != 0:
                raise ValueError("La reponse LM Studio contient un raisonnement ou est incomplete.")
            if not isinstance(contenu, str):
                raise ValueError("La reponse LM Studio ne contient pas de texte.")
            texte = contenu.strip()[:EXPLICATION_MAX_CARACTERES]
            if len(texte) < 15:
                raise ValueError("La reponse LM Studio est vide.")
        except (httpx.HTTPError, AttributeError, IndexError, KeyError, TypeError, ValueError) as exc:
            metriques.enregistrer(
                "/v1/chat/completions", statut, (time.perf_counter() - debut) * 1000
            )
            metriques.incrementer("erreurs_reformulation")
            metriques.incrementer("replis_texte_assemble")
            metriques.deverser(MONITORING_MODEL / "metriques_lm_studio.json")
            log.warning(
                "Reformulation locale indisponible",
                extra={"event": "reformulation_indisponible", "erreur_type": type(exc).__name__},
            )
            raise ServiceIADisponible("LM Studio ne peut pas reformuler ce verdict.") from exc

        metriques.enregistrer(
            "/v1/chat/completions", statut, (time.perf_counter() - debut) * 1000
        )
        metriques.incrementer("reformulations_modele_local")
        metriques.deverser(MONITORING_MODEL / "metriques_lm_studio.json")
        log.info("Verdict reformule localement", extra={"event": "verdict_reformule"})
        return texte
