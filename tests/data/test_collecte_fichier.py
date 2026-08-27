"""Preuve C1 : les fichiers locaux sont controles avant la chaine."""

import json
import tempfile
from pathlib import Path

import pytest

from concorde.collect.base import MANIFEST_PATH
from concorde.collect.fichier import CollecteurDVF


def test_collecteur_dvf_ecrit_une_source_fichier_rejouable(tmp_path: Path) -> None:
    """Detecte une collecte DVF qui ne produirait plus son artefact C1."""
    resultat = CollecteurDVF(destination=tmp_path).collecter(mode="samples")

    assert resultat.succes
    assert resultat.type_source == "fichier"
    assert resultat.nb_lignes > 0
    assert (tmp_path / "dvf.parquet").exists()


def test_collecteur_dvf_signale_un_schema_incomplet(tmp_path: Path) -> None:
    """Detecte un fichier DVF accepte malgre une colonne metier manquante."""
    source = tmp_path / "dvf-incomplet.csv"
    source.write_text("id_mutation,date_mutation\nmutation-1,2025-01-01\n", encoding="utf-8")

    resultat = CollecteurDVF(source=source, destination=tmp_path).collecter()

    assert not resultat.succes
    assert "colonnes obligatoires absentes" in (resultat.erreur or "")


@pytest.mark.regression
def test_une_collecte_en_repertoire_temporaire_ne_touche_pas_le_manifeste_reel() -> None:
    """Verrouille l'isolation du manifeste de demonstration. (C1, C3)

    Un test qui provoque volontairement un echec de collecte ecrivait son
    echec dans `data/raw/_manifest.json` : la suite de tests corrompait
    l'artefact montre au jury, qui passait de 1 743 lignes a 746.
    """
    avant = MANIFEST_PATH.read_text(encoding="utf-8") if MANIFEST_PATH.exists() else None

    with tempfile.TemporaryDirectory() as repertoire:
        ailleurs = Path(repertoire)
        source = ailleurs / "dvf-incomplet.csv"
        source.write_text("id_mutation,date_mutation\nmutation-1,2025-01-01\n", encoding="utf-8")

        resultat = CollecteurDVF(source=source, destination=ailleurs).collecter()

        assert not resultat.succes
        # L'echec est trace, mais a cote des donnees qu'il decrit.
        assert (ailleurs / "_manifest.json").exists()
        assert "dvf" in json.loads((ailleurs / "_manifest.json").read_text(encoding="utf-8"))

    apres = MANIFEST_PATH.read_text(encoding="utf-8") if MANIFEST_PATH.exists() else None
    assert apres == avant, "la collecte en repertoire temporaire a modifie le manifeste reel"
