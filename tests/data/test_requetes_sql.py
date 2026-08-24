"""Preuves C2 : requetes executees sur PostgreSQL et Spark SQL."""

from concorde.queries import executer_requete_postgres, executer_requete_spark


def test_requete_postgres_joint_communes_et_aleas() -> None:
    """Detecte une jointure SGBD cassée ou un filtre departement ignore."""
    resultat = executer_requete_postgres("33")

    assert resultat.to_dict(orient="records") == [
        {"code_commune": "33063", "nom_commune": "BORDEAUX", "alea_max": 3, "nb_aleas_significatifs": 2}
    ]


def test_requete_spark_sql_agrege_les_dpe_par_commune() -> None:
    """Detecte une lecture hors Spark SQL ou une agregation DPE modifiee."""
    resultat = executer_requete_spark()

    assert set(resultat.columns) == {"code_commune", "nb_dpe", "conso_moyenne"}
    assert len(resultat) == 3
    assert int(resultat["nb_dpe"].sum()) == 726
