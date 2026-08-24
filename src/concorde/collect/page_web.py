"""Collecte depuis une page web publique ciblee : Géorisques. (C1)

Le snapshot HTML versionne est une preuve rejouable du scraping. Le mode en
ligne est volontairement minimal, lent et identifie : il ne sert qu'a mettre a
jour la capture apres verification humaine des conditions d'utilisation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import httpx
import pandas as pd
from bs4 import BeautifulSoup

from concorde.collect.base import Collecteur
from concorde.common.config import get_settings
from concorde.common.offline import OfflineViolation
from concorde.common.paths import DATA_SAMPLES

PAGE_GEOLOGIE = "https://www.georisques.gouv.fr/risques/retrait-gonflement-des-argiles"
CACHE_PAGE = DATA_SAMPLES / "georisques_page_sample.html"
ModeCollecte = Literal["samples", "online"]


def _extraire_cartes(html: str, url: str) -> pd.DataFrame:
    soup = BeautifulSoup(html, "lxml")
    cartes = soup.select("article.risk-card")
    if not cartes:
        cartes = soup.select("main article")
    lignes = [
        {
            "titre_page": soup.find("h1").get_text(" ", strip=True) if soup.find("h1") else "",
            "theme": carte.find(["h2", "h3"]).get_text(" ", strip=True)
            if carte.find(["h2", "h3"])
            else "",
            "extrait": carte.find("p").get_text(" ", strip=True) if carte.find("p") else "",
            "url_source": url,
        }
        for carte in cartes
    ]
    if not lignes:
        raise ValueError("Aucune carte de risque extraite de la page ciblee")
    return pd.DataFrame(lignes)


class CollecteurPageGeorisques(Collecteur):
    """Scrape une page Géorisques ou son snapshot local."""

    nom = "page_georisques"
    type_source = "page_web"
    origine = "Géorisques (BRGM / ministère) — page information preventive"

    def __init__(self, mode: ModeCollecte = "samples", source: Path | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.mode = mode
        self.source = source or CACHE_PAGE

    def _collecter(self) -> pd.DataFrame:
        if self.mode == "samples":
            if not self.source.exists():
                raise FileNotFoundError(f"Snapshot Géorisques introuvable : {self.source}")
            return _extraire_cartes(self.source.read_text(encoding="utf-8"), str(self.source))

        if get_settings().offline:
            raise OfflineViolation("Scraping Géorisques refuse : CONCORDE_OFFLINE=true")
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            reponse = client.get(PAGE_GEOLOGIE, headers={"User-Agent": "Concorde-RNCP/0.1"})
            reponse.raise_for_status()
        return _extraire_cartes(reponse.text, PAGE_GEOLOGIE)
