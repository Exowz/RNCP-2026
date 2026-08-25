"""Contrat de l'API data REST. (C5)"""

from api.data.main import app
from api.model.schemas import RapprochementEntree
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


def test_liste_rapprochements_filtre_et_expose_les_noms_utiles() -> None:
    """Detecte une liste front inutilisable car filtree ou anonymisee par des codes."""
    with TestClient(app) as client:
        reponse = client.get(
            "/rapprochements",
            params={
                "code_commune": "17300",
                "niveau_confiance": "insuffisant",
                "avec_dpe": "false",
                "page": 1,
                "taille": 3,
            },
            headers={"X-API-Key": "dev-reader-key"},
        )

    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["total"] > 0
    assert len(corps["resultats"]) <= 3
    assert all(item["code_commune"] == "17300" for item in corps["resultats"])
    assert all(item["nom_commune"] == "ROCHEFORT" for item in corps["resultats"])
    assert all(item["a_dpe"] is False for item in corps["resultats"])
    assert all(item["niveau_confiance"] == "insuffisant" for item in corps["resultats"])


def test_detail_rapprochement_fournit_une_charge_predict_et_sa_presentation() -> None:
    """Detecte un detail qui ne peut plus alimenter /predict ou qui masque les noms."""
    with TestClient(app) as client:
        reponse = client.get("/rapprochements/2023-100021", headers={"X-API-Key": "dev-reader-key"})

    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["presentation"]["nom_commune"] == "ANNESSE-ET-BEAULIEU"
    assert corps["presentation"]["etiquette_dpe"] == "E"
    assert corps["presentation"]["adresse_ban"].startswith("48 ALLEE DES CHENES")
    entree = RapprochementEntree.model_validate(corps["donnees"])
    assert entree.id_mutation == "2023-100021"


def test_demonstration_reutilise_cinq_cas_reels_et_les_rend_comprehensibles() -> None:
    """Detecte une demonstration incomplete, inventee ou limitee aux identifiants techniques."""
    with TestClient(app) as client:
        reponse = client.get("/rapprochements/demonstration", headers={"X-API-Key": "dev-reader-key"})

    assert reponse.status_code == 200
    cas = reponse.json()["cas"]
    assert {item["identifiant"] for item in cas} == {
        "coherent",
        "ecart_surface",
        "dpe_posterieur",
        "parcelle_ambigue",
        "sans_dpe",
    }
    assert all(item["presentation"]["nom_commune"] for item in cas)
    assert all("donnees" in item for item in cas)
