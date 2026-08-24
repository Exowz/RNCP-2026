"""Preuve C8 : le service IA local est joignable et configure."""

import pytest

from concorde.service.lm_studio import ClientLMStudio

pytestmark = pytest.mark.local_service


def test_lm_studio_expose_le_modele_local_retenu() -> None:
    """Detecte un serveur absent ou le dechargement du modele retenu."""
    etat = ClientLMStudio().verifier_service()

    assert etat["modele"] == "google/gemma-4-e4b"
    assert etat["disponible"] is True
