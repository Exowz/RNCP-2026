"""Preuve C11 : rapport Evidently produit hors ligne."""

from concorde.monitoring_modele import generer_rapport_derives


def test_rapport_evidently_ecrit_html_et_json(tmp_path) -> None:
    """Detecte une regression qui ne produirait plus de preuve de derive."""
    resultat = generer_rapport_derives(tmp_path)

    assert resultat["reference_lignes"] > 0
    assert resultat["courant_lignes"] > 0
    assert (tmp_path / "evidently_drift.html").exists()
    assert (tmp_path / "evidently_drift.json").exists()
