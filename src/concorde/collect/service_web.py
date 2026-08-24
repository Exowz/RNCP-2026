"""Collecte depuis un service web : Base Adresse Nationale. (C1)

Le cache JSON est une reponse capturee de l'API BAN. Il permet de rejouer le
contrat HTTP sans Internet ; le mode `online` reste explicite et refuse de
contourner la contrainte `CONCORDE_OFFLINE=true`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

import httpx
import pandas as pd

from concorde.collect.base import Collecteur
from concorde.common.config import get_settings
from concorde.common.offline import OfflineViolation
from concorde.common.paths import DATA_SAMPLES

BAN_ENDPOINT = "https://api-adresse.data.gouv.fr/search/"
CACHE_BAN = DATA_SAMPLES / "ban_reponse_sample.json"
ModeCollecte = Literal["samples", "online"]


def _vers_lignes_ban(reponse: dict) -> pd.DataFrame:
    """Aplati la reponse GeoJSON BAN en table sans conserver d'adresse personnelle."""
    lignes = []
    for feature in reponse.get("features", []):
        prop = feature.get("properties", {})
        lignes.append(
            {
                "identifiant_ban": prop.get("id"),
                "libelle": prop.get("label"),
                "score_ban": prop.get("score"),
                "code_commune": str(prop.get("citycode", "")).zfill(5),
                "code_postal": str(prop.get("postcode", "")),
                "type_resultat": prop.get("type"),
            }
        )
    return pd.DataFrame(lignes)


class CollecteurBAN(Collecteur):
    """Interroge la BAN ou rejoue sa capture JSON versionnee."""

    nom = "ban"
    type_source = "service_web"
    origine = "Base Adresse Nationale (DINUM / IGN) — API adresse.data.gouv.fr"

    def __init__(self, mode: ModeCollecte = "samples", source: Path | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.mode = mode
        self.source = source or CACHE_BAN

    def _collecter(self) -> pd.DataFrame:
        if self.mode == "samples":
            if not self.source.exists():
                raise FileNotFoundError(f"Capture BAN introuvable : {self.source}")
            return _vers_lignes_ban(json.loads(self.source.read_text(encoding="utf-8")))

        if get_settings().offline:
            raise OfflineViolation("Collecte BAN en ligne refusee : CONCORDE_OFFLINE=true")
        with httpx.Client(timeout=10.0, follow_redirects=False) as client:
            reponse = client.get(BAN_ENDPOINT, params={"q": "Bordeaux", "limit": 3})
            reponse.raise_for_status()
        return _vers_lignes_ban(reponse.json())
