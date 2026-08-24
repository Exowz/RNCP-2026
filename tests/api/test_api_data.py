"""Contrat de l'API data REST. (C5)"""

from api.data.main import app
from fastapi.testclient import TestClient


def test_api_data_exige_une_cle_puis_filtre_les_communes() -> None:
    """Detecte une fuite de donnees ou un filtre departement qui ne s'applique plus."""
    with TestClient(app) as client:
        assert client.get("/communes").status_code == 401

        reponse = client.get("/communes", params={"departement": "33"}, headers={"X-API-Key": "dev-reader-key"})

    assert reponse.status_code == 200
    assert reponse.json() == [
        {"code_commune": "33063", "nom_commune": "BORDEAUX", "alea_max": 3, "nb_aleas_significatifs": 2}
    ]
