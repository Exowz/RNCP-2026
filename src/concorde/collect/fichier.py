"""Collecte de type **fichier de donnees**. (C1)

Source metier : DVF+ — transactions immobilieres geolocalisees, publiees par la
DGALN / Cerema sur data.gouv.fr. Une ligne par mutation.

Deux modes, un seul code :

- `origine="samples"` : lit l'extrait fige de `data/samples/`. C'est le mode de
  la demonstration hors ligne et des tests, deterministe par construction.
- `origine=<chemin>` : lit un fichier telecharge dans `data/external/`.

Le schema attendu est verifie a la lecture : une colonne obligatoire absente
fait echouer la collecte immediatement, avec le nom de la colonne. Detecter le
probleme ici coute une seconde ; le detecter apres le nettoyage coute une heure.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from concorde.collect.base import Collecteur
from concorde.collect.spark_dpe import lire_dpe_par_spark
from concorde.common.paths import DATA_SAMPLES

#: Colonnes DVF+ indispensables a la suite de la chaine.
COLONNES_DVF_REQUISES: tuple[str, ...] = (
    "id_mutation",
    "date_mutation",
    "valeur_fonciere",
    "code_commune",
    "nom_commune",
    "id_parcelle",
    "type_local",
    "surface_reelle_bati",
)

#: Colonnes ADEME indispensables (noms officiels de l'Observatoire DPE-Audit).
COLONNES_DPE_REQUISES: tuple[str, ...] = (
    "N°DPE",
    "Date_établissement_DPE",
    "Etiquette_DPE",
    "Surface_habitable_logement",
    "Code_INSEE_(BAN)",
    "id_parcelle_rapprochee",
)


class ColonnesManquantes(ValueError):
    """Le fichier source ne porte pas le schema attendu."""


def _verifier_schema(df: pd.DataFrame, requises: tuple[str, ...], source: str) -> None:
    manquantes = [c for c in requises if c not in df.columns]
    if manquantes:
        raise ColonnesManquantes(
            f"{source} : colonnes obligatoires absentes {manquantes}. "
            f"Colonnes presentes : {list(df.columns)[:12]}..."
        )


class CollecteurDVF(Collecteur):
    """Mutations DVF+ depuis un fichier CSV."""

    nom = "dvf"
    type_source = "fichier"
    origine = "DVF+ (DGALN / Cerema, data.gouv.fr) — extrait CSV local"

    def __init__(self, source: Path | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.source = source or DATA_SAMPLES / "dvf_sample.csv"

    def _collecter(self) -> pd.DataFrame:
        if not self.source.exists():
            raise FileNotFoundError(
                f"Fichier DVF introuvable : {self.source}. "
                "Executer `python scripts/make_sample_fixture.py` pour regenerer les extraits."
            )
        df = pd.read_csv(self.source, dtype={"code_commune": str, "code_postal": str,
                                             "code_departement": str, "code_type_local": str})
        _verifier_schema(df, COLONNES_DVF_REQUISES, "DVF+")
        return df


class CollecteurDPE(Collecteur):
    """Diagnostics ADEME lus par Spark depuis un extrait CSV local."""

    nom = "dpe"
    type_source = "big_data"
    origine = "Observatoire DPE-Audit (ADEME) — extrait CSV local lu par Spark"

    def __init__(self, source: Path | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.source = source or DATA_SAMPLES / "dpe_ademe_sample.csv"

    def _collecter(self) -> pd.DataFrame:
        if not self.source.exists():
            raise FileNotFoundError(
                f"Fichier DPE introuvable : {self.source}. "
                "Executer `python scripts/make_sample_fixture.py` pour regenerer les extraits."
            )
        df = lire_dpe_par_spark(self.source)
        for colonne in ("Code_INSEE_(BAN)", "Code_postal_(BAN)", "N°DPE"):
            if colonne in df:
                df[colonne] = df[colonne].astype(str)
        _verifier_schema(df, COLONNES_DPE_REQUISES, "DPE ADEME")
        return df


class CollecteurAleas(Collecteur):
    """Exposition aux aleas naturels par commune.

    Extrait fige du service Georisques (BRGM). Sur la tranche verticale il est
    lu depuis un fichier ; l'appel HTTP reel a l'API est branche en C1 via
    `collect/service_web.py`, avec ce meme extrait comme cache hors ligne.
    """

    nom = "aleas"
    type_source = "fichier"
    origine = "Georisques (BRGM / MTE) — extrait fige"

    def __init__(self, source: Path | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.source = source or DATA_SAMPLES / "georisques_sample.csv"

    def _collecter(self) -> pd.DataFrame:
        if not self.source.exists():
            raise FileNotFoundError(f"Fichier aleas introuvable : {self.source}")
        return pd.read_csv(self.source, dtype={"code_commune": str})
