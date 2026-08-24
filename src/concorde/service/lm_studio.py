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
metriques = Metriques(SERVICE)
log = setup_logging(SERVICE)


class ServiceIADisponible(RuntimeError):
    """Leve lorsque LM Studio ou le modele retenu n'est pas disponible."""


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
