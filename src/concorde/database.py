"""Initialisation et acces a PostgreSQL local. (C1, C2, C4)"""

from __future__ import annotations

import csv
from collections.abc import Iterator
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row

from concorde.common.config import Settings, get_settings
from concorde.common.paths import DATA_SAMPLES, DOCS_DIR

SCHEMA_SQL = DOCS_DIR / "sql" / "schema.sql"
COMMUNES_CSV = DATA_SAMPLES / "communes_reference.csv"
ALEAS_CSV = DATA_SAMPLES / "georisques_sample.csv"
NIVEAUX_ALEA = {"Nul": 0, "Tres faible": 1, "Faible": 2, "Modere": 3, "Moyen": 3, "Fort": 4}


def _conninfo(reglages: Settings) -> str:
    return (
        f"host={reglages.pg_host} port={reglages.pg_port} dbname={reglages.pg_db} "
        f"user={reglages.pg_user} password={reglages.pg_password} connect_timeout=3"
    )


@contextmanager
def connexion_postgresql(reglages: Settings | None = None) -> Iterator[psycopg.Connection]:
    """Ouvre une connexion locale courte, sans reutiliser de mot de passe en clair."""
    with psycopg.connect(_conninfo(reglages or get_settings()), row_factory=dict_row) as connexion:
        yield connexion


def initialiser_et_importer() -> int:
    """Applique le MPD puis importe les trois communes de demonstration."""
    with connexion_postgresql() as connexion:
        connexion.execute(SCHEMA_SQL.read_text(encoding="utf-8"))
        with COMMUNES_CSV.open(encoding="utf-8", newline="") as fichier:
            lignes = list(csv.DictReader(fichier))
        with connexion.cursor() as curseur:
            curseur.executemany(
                """
                INSERT INTO reference_commune (code_commune, nom_commune, code_postal, departement)
                VALUES (%(code_commune)s, %(nom_commune)s, %(code_postal)s, %(departement)s)
                ON CONFLICT (code_commune) DO UPDATE SET
                  nom_commune = EXCLUDED.nom_commune,
                  code_postal = EXCLUDED.code_postal,
                  departement = EXCLUDED.departement
                """,
                lignes,
            )
        with ALEAS_CSV.open(encoding="utf-8", newline="") as fichier:
            aleas = [
                {
                    "code_commune": ligne["code_commune"].zfill(5),
                    "type_alea": ligne["type_alea"],
                    "niveau": NIVEAUX_ALEA[ligne["niveau_alea"]],
                }
                for ligne in csv.DictReader(fichier)
            ]
        with connexion.cursor() as curseur:
            curseur.executemany(
                """
                INSERT INTO exposition_alea (code_commune, type_alea, niveau)
                VALUES (%(code_commune)s, %(type_alea)s, %(niveau)s)
                ON CONFLICT (code_commune, type_alea) DO UPDATE SET niveau = EXCLUDED.niveau
                """,
                aleas,
            )
        connexion.commit()
    return len(lignes)
