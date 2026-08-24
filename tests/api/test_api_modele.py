"""Contrat C9 de l'API modele : auth, validation et prediction."""

from api.model.main import app
from app.exemples import charger
from fastapi.testclient import TestClient


def test_predict_refuse_un_appel_sans_cle_api() -> None:
    """Detecte une route de prediction exposee sans authentification."""
    charge = charger()["coherent"]["donnees"]

    with TestClient(app) as client:
        reponse = client.post("/predict", json=charge)

    assert reponse.status_code == 401


def test_predict_valide_et_retourne_les_trois_axes_du_verdict() -> None:
    """Detecte une rupture du contrat prediction/coherence/confiance."""
    charge = charger()["coherent"]["donnees"]

    with TestClient(app) as client:
        reponse = client.post("/predict", json=charge, headers={"X-API-Key": "dev-reader-key"})

    assert reponse.status_code == 200
    verdict = reponse.json()
    assert verdict["statut"] == "evalue"
    assert 0 <= verdict["score_anomalie"] <= 1
    assert 0 <= verdict["score_coherence"] <= 1
    assert verdict["confiance"]["niveau"] in {"eleve", "moyen", "faible", "insuffisant"}


def test_predict_rejette_un_champ_inconnu() -> None:
    """Detecte une validation permissive qui masquerait une erreur client."""
    charge = charger()["coherent"]["donnees"] | {"prix_predit": 200000}

    with TestClient(app) as client:
        reponse = client.post("/predict", json=charge, headers={"X-API-Key": "dev-reader-key"})

    assert reponse.status_code == 422
