"""Preuves d'integration de la demonstration hors ligne."""

import socket

import pytest
from api.model.main import app
from fastapi.testclient import TestClient

from concorde.common.offline import OfflineViolation, disable_offline_guard, is_guard_active


def test_demarrage_api_active_le_verrou_reseau_hors_ligne() -> None:
    """Empeche qu'un futur changement laisse l'API joindre Internet en demo.

    La mutation ``enable_offline_guard()`` retiree du cycle de vie doit faire
    echouer ce test : le modele peut alors sembler local tout en telechargeant
    une dependance oubliee le jour de la soutenance.
    """
    disable_offline_guard()

    with TestClient(app) as client:
        assert client.get("/sante").status_code == 200
        assert is_guard_active()
        with pytest.raises(OfflineViolation, match="Sortie reseau bloquee"):
            socket.getaddrinfo("example.org", 443)

    disable_offline_guard()
