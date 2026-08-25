"""C21 : non-regression de l'ordre d'initialisation PostgreSQL."""

import pytest

from concorde.collect.base_de_donnees import CollecteurPostgreSQL
from concorde.database import initialiser_et_importer


@pytest.mark.regression
def test_import_postgresql_precede_et_rend_possible_la_collecte() -> None:
    """Detecte le retour de l'incident UndefinedTable avant la collecte C1."""
    assert initialiser_et_importer() == 3

    resultat = CollecteurPostgreSQL().collecter()

    assert resultat.succes
    assert resultat.nb_lignes == 3
