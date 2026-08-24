"""Preuve C1 : lecture d'une source PostgreSQL locale."""

from concorde.collect.base_de_donnees import CollecteurPostgreSQL


def test_collecteur_postgresql_lit_les_references_communales() -> None:
    """Detecte une base absente, un import incomplet ou une requete C1 cassee."""
    resultat = CollecteurPostgreSQL().collecter()

    assert resultat.succes
    assert resultat.type_source == "base_de_donnees"
    assert resultat.nb_lignes == 3
