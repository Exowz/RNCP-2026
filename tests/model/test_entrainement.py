"""Contrat C12 : entrainement, evaluation et artefact servent ensemble."""

from pathlib import Path

import pytest

from concorde.clean.rapprochement import SORTIE
from concorde.model.entrainement import entrainer_et_geler
from concorde.model.moteur import Moteur


@pytest.mark.model
@pytest.mark.slow
def test_entrainement_evalue_et_produit_un_artefact_rechargeable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Detecte un entrainement qui n'evalue plus ou produit un artefact inutilisable."""
    import concorde.model.entrainement as entrainement

    artefact = tmp_path / "moteur.pt"
    monkeypatch.setattr(entrainement, "FICHE_MD", tmp_path / "fiche-modele.md")
    monkeypatch.setattr(entrainement, "METRIQUES_JSON", tmp_path / "metriques.json")
    monkeypatch.setattr(entrainement, "_journaliser_mlflow", lambda *args: None)

    moteur, metriques = entrainer_et_geler(table=SORTIE, chemin_artefact=artefact)

    assert artefact.exists()
    assert moteur.fiche.nb_lignes_entrainement > 0
    assert metriques["nb_test"] > 0
    assert 0 <= metriques["taux_signalement_atypique"] <= 1
    assert Moteur.charger(artefact).fiche.empreinte_donnees == moteur.fiche.empreinte_donnees
