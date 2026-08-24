"""Requetes C2 executees sur PostgreSQL et Spark SQL."""

from __future__ import annotations

import pandas as pd
from pyspark.sql import SparkSession

from concorde.common.paths import DATA_RAW
from concorde.database import connexion_postgresql


def executer_requete_postgres(departement: str) -> pd.DataFrame:
    """Joint les communes et aleas, filtre par departement indexe."""
    with connexion_postgresql() as connexion:
        lignes = connexion.execute(
            """
            SELECT c.code_commune, c.nom_commune,
                   COALESCE(MAX(a.niveau), 0) AS alea_max,
                   COUNT(*) FILTER (WHERE a.niveau >= 3) AS nb_aleas_significatifs
            FROM reference_commune AS c
            LEFT JOIN exposition_alea AS a USING (code_commune)
            WHERE c.departement = %s
            GROUP BY c.code_commune, c.nom_commune
            ORDER BY c.code_commune
            """,
            (departement,),
        ).fetchall()
    return pd.DataFrame(lignes)


def executer_requete_spark() -> pd.DataFrame:
    """Agrege les DPE par commune en Spark SQL depuis le Parquet brut."""
    spark = (
        SparkSession.builder.master("local[1]")
        .appName("concorde-requete-dpe")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", "1")
        .getOrCreate()
    )
    try:
        spark.read.parquet(str(DATA_RAW / "dpe.parquet")).createOrReplaceTempView("dpe")
        return spark.sql(
            """
            SELECT `Code_INSEE_(BAN)` AS code_commune,
                   COUNT(*) AS nb_dpe,
                   ROUND(AVG(CAST(`Conso_5_usages_par_m²_é_primaire` AS DOUBLE)), 2) AS conso_moyenne
            FROM dpe
            WHERE `Code_INSEE_(BAN)` IS NOT NULL
            GROUP BY `Code_INSEE_(BAN)`
            ORDER BY code_commune
            """
        ).toPandas()
    finally:
        spark.stop()
