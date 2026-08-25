"""Preuve C3 : nettoyage et rapprochement des fixtures versionnees."""

from pathlib import Path

import pandas as pd
import pytest

import concorde.clean.rapprochement as rapprochement


@pytest.mark.data
def test_rapprochement_conserve_les_mutations_sans_dpe(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Detecte une jointure interne qui ferait disparaitre les inconnues assumees."""
    dvf = pd.read_csv("data/samples/dvf_sample.csv", dtype={"code_commune": str})
    dpe = pd.read_csv("data/samples/dpe_ademe_sample.csv").iloc[0:0]
    aleas = pd.read_csv("data/samples/georisques_sample.csv", dtype={"code_commune": str})
    monkeypatch.setattr(rapprochement, "SORTIE", tmp_path / "rapprochements.parquet")
    monkeypatch.setattr(rapprochement, "RAPPORT_JSON", tmp_path / "nettoyage.json")
    monkeypatch.setattr(rapprochement, "RAPPORT_MD", tmp_path / "nettoyage.md")

    resultat, rapports = rapprochement.construire(dvf=dvf, dpe=dpe, aleas=aleas, ecrire=True)

    assert len(resultat) > 0
    assert not resultat["a_dpe"].any()
    assert len(rapports) == 2
    assert (tmp_path / "rapprochements.parquet").exists()
    assert (tmp_path / "nettoyage.json").exists()
    assert "Sans DPE" in (tmp_path / "nettoyage.md").read_text(encoding="utf-8")
