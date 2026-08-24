"""Contrat hors ligne de l'application web."""

from app.main import app
from fastapi.testclient import TestClient

from concorde.common.offline import disable_offline_guard, is_guard_active


def test_demarrage_app_active_le_verrou_reseau_hors_ligne() -> None:
    """Evite qu'une future ressource web ou CDN casse la demo sans Internet."""
    disable_offline_guard()

    with TestClient(app) as client:
        assert client.get("/").status_code == 200
        assert is_guard_active()

    disable_offline_guard()
