"""Lecture Spark SQL de l'extrait DPE ADEME. (C1, C2)

La demonstration utilise un extrait local, mais sa lecture suit le meme moteur
Spark que le jeu ADEME en Parquet : c'est la preuve du chemin big data sans
telecharger plusieurs gigaoctets le jour de la soutenance.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from pyspark.sql import SparkSession


def lire_dpe_par_spark(source: Path) -> pd.DataFrame:
    """Lit un export DPE CSV local avec Spark et le restitue a la collecte.

    La session est volontairement bornee a un coeur et arretee apres lecture :
    le test et la demo restent legers, sans laisser de JVM en arriere-plan.
    """
    if not source.exists():
        raise FileNotFoundError(f"Extrait DPE introuvable : {source}")

    spark = (
        SparkSession.builder.master("local[1]")
        .appName("concorde-collecte-dpe")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", "1")
        .getOrCreate()
    )
    try:
        dpe_spark = spark.read.option("header", "true").option("encoding", "UTF-8").csv(str(source))
        return dpe_spark.toPandas()
    finally:
        spark.stop()
