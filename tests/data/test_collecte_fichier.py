"""Preuve C1 : les fichiers locaux sont controles avant la chaine."""

from pathlib import Path

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
