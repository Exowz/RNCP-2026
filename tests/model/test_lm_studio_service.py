"""Preuve C8 : le service IA local est joignable et configure."""

import pytest

from concorde.service.lm_studio import ClientLMStudio, ServiceIADisponible

pytestmark = pytest.mark.local_service

VERDICT_REDUIT = {
    "statut": "evalue",
    "niveau_anomalie": "a_verifier",
    "score_coherence": 0.62,
    "motifs": [
        {
            "identifiant": "surface_incoherente",
            "libelle": "Surface incoherente",
            "gravite": "majeur",
            "message": "La surface declaree par les deux sources differe nettement.",
        }
    ],
    "confiance": {
        "score": 0.72,
        "niveau": "moyen",
        "reserves": [
            {"identifiant": "ban", "message": "Le rapprochement geographique reste prudent.", "penalite": 0.1}
        ],
    },
    "explication": "Une verification de la surface est necessaire avant toute reutilisation.",
}


def test_lm_studio_expose_le_modele_local_retenu() -> None:
    """Detecte un serveur absent ou le dechargement du modele retenu."""
    etat = ClientLMStudio().verifier_service()

    assert etat["modele"] == "google/gemma-4-e4b"
    assert etat["disponible"] is True


def test_reformuler_verdict_reste_optionnel_sur_le_service_reel() -> None:
    """Le test local constate une reponse ou un repli, jamais une panne de l'application."""
    try:
        texte = ClientLMStudio().reformuler_verdict(VERDICT_REDUIT)
    except ServiceIADisponible:
        source = "texte_assemble"
    else:
        assert 15 <= len(texte) <= 1000
        source = "modele_local"

    assert source in {"modele_local", "texte_assemble"}
