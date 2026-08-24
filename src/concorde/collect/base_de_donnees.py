"""Collecte depuis PostgreSQL local. (C1)"""

from __future__ import annotations

import pandas as pd

from concorde.collect.base import Collecteur
from concorde.database import connexion_postgresql


class CollecteurPostgreSQL(Collecteur):
    """Extrait les references communales depuis le SGBD du projet."""

    nom = "communes_postgres"
    type_source = "base_de_donnees"
    origine = "PostgreSQL local Concorde — table reference_commune"

    def _collecter(self) -> pd.DataFrame:
        with connexion_postgresql() as connexion:
            lignes = connexion.execute(
                """
                SELECT code_commune, nom_commune, code_postal, departement
                FROM reference_commune
                ORDER BY code_commune
                """
            ).fetchall()
        return pd.DataFrame(lignes)
