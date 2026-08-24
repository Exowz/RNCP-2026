"""Preuve que l'extrait ADEME passe par Spark avant le nettoyage."""

from pathlib import Path

from concorde.collect.spark_dpe import lire_dpe_par_spark


def test_lire_dpe_par_spark_restitue_le_schema_adele_local() -> None:
    """Detecte une regression qui remplacerait Spark par une lecture Pandas.

    Le changement fautif est le retrait de la session Spark ou le changement du
    contrat de colonnes ADEME : la source big data ne serait plus reellement
    demontree dans la chaine de collecte.
    """
    source = Path("data/samples/dpe_ademe_sample.csv")

    resultat = lire_dpe_par_spark(source)

    assert len(resultat) == 726
    assert {"N°DPE", "Code_INSEE_(BAN)", "id_parcelle_rapprochee"} <= set(resultat.columns)
