"""Contrat C9 de l'API modele : auth, validation et prediction."""

from api.model import main as api_modele
from api.model.main import app
from app.exemples import charger
from fastapi.testclient import TestClient

from concorde.service.lm_studio import ServiceIADisponible


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


def test_sante_pose_les_entetes_de_securite_et_reprend_la_correlation() -> None:
    """Evite une reponse API sans protection navigateur ni trace exploitable."""
    request_id = "preuve-c17-correlation"

    with TestClient(app) as client:
        reponse = client.get("/sante", headers={"X-Request-ID": request_id})

    assert reponse.status_code == 200
    assert reponse.headers["X-Request-ID"] == request_id
    assert reponse.headers["X-Content-Type-Options"] == "nosniff"
    assert reponse.headers["X-Frame-Options"] == "DENY"
    assert "default-src 'self'" in reponse.headers["Content-Security-Policy"]


def test_expliquer_replie_sur_texte_assemble_si_lm_studio_est_absent(monkeypatch) -> None:
    """Le parcours particulier reste disponible quand le service optionnel manque."""
    def _absent(*_args, **_kwargs):
        raise ServiceIADisponible("LM Studio absent pour ce test")

    client_absent = type("ClientAbsent", (), {"reformuler_verdict": _absent})
    monkeypatch.setattr(api_modele, "ClientLMStudio", client_absent, raising=False)
    charge = charger()["coherent"]["donnees"]

    with TestClient(app) as client:
        verdict = client.post("/predict", json=charge, headers={"X-API-Key": "dev-reader-key"})
        assert verdict.status_code == 200
        donnees = verdict.json()
        projection = {
            cle: donnees[cle]
            for cle in ("statut", "niveau_anomalie", "score_coherence", "motifs", "confiance", "explication")
        }
        reponse = client.post("/expliquer", json=projection, headers={"X-API-Key": "dev-reader-key"})

    assert reponse.status_code == 200
    assert reponse.json() == {"texte": projection["explication"], "source": "texte_assemble"}
