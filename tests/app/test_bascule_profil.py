"""Non-regression de la bascule de profil. (C10, C21)

Incident APP-2026-08-25 : depuis la page de resultat, les liens de profil du
bandeau pointaient sur `?profil=...`, donc sur un **GET** de la page courante.
`/evaluer` n'acceptant que POST, le clic renvoyait `405 Method Not Allowed` en
JSON brut, en plein milieu du parcours de demonstration.

Ces tests fixent le contrat corrige : la bascule de profil doit rester une
navigation HTML, sur toutes les pages, et conserver le cas evalue.
"""

from typing import Any

import pytest
from app.main import app
from fastapi.testclient import TestClient

from concorde.common.offline import disable_offline_guard
from concorde.model import regles_coherence
from concorde.model.moteur import Moteur


@pytest.fixture(autouse=True)
def sans_transport_http(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remplace le transport HTTP vers l'API modele par un appel direct au moteur.

    Ces tests portent sur le **routage et le rendu** : ils verifient qu'un GET
    sur `/evaluer` rend du HTML plutot qu'un 405, et que la bascule de profil
    conserve le cas. Ils ne portent pas sur le transport HTTP.

    Sans cette doublure, ils dependent d'une API modele demarree sur le port
    8002. Elle tourne sur le poste de developpement, jamais en integration
    continue : les tests passaient en local et echouaient en CI avec un 503,
    pour une raison etrangere a ce qu'ils verifient. C'est precisement le defaut
    qu'ils sont censes empecher chez les autres.

    La doublure conserve le **vrai moteur** — seul le saut reseau est retire.
    L'appel HTTP reel reste prouve ailleurs : par la sonde `/sante` de
    l'application, qui interroge son amont, et par la demonstration.
    """
    moteur = Moteur.charger()

    class ClientDouble:
        def __init__(self, *_: Any, **__: Any) -> None:
            pass

        def evaluer(self, rapprochement: dict[str, Any]) -> dict[str, Any]:
            return moteur.predire_un(rapprochement)

        def fiche_modele(self) -> dict[str, Any]:
            return moteur.fiche.en_dict()

        def regles(self) -> list[dict[str, str]]:
            return regles_coherence.catalogue()

        def sante(self) -> dict[str, Any]:
            return {"statut": "ok", "service": "api-model",
                    "version_modele": moteur.fiche.version,
                    "modele_charge": True, "hors_ligne": True}

    monkeypatch.setattr("app.main.ClientModele", ClientDouble)


@pytest.mark.regression
def test_evaluer_repond_en_get_et_ne_renvoie_pas_405() -> None:
    """Reproduit l'incident : un GET sur /evaluer doit rendre du HTML, pas 405."""
    disable_offline_guard()

    with TestClient(app) as client:
        reponse = client.get("/evaluer", params={"profil": "analyste", "cas": "ecart_surface"})

    assert reponse.status_code == 200, (
        f"GET /evaluer a renvoye {reponse.status_code} : la bascule de profil casse "
        "sur la page de resultat."
    )
    assert reponse.headers["content-type"].startswith("text/html")
    assert "Method Not Allowed" not in reponse.text

    disable_offline_guard()


@pytest.mark.regression
def test_les_liens_de_profil_conservent_le_cas_evalue() -> None:
    """Basculer de profil doit rejouer le meme rapprochement, pas en perdre le fil."""
    disable_offline_guard()

    with TestClient(app) as client:
        reponse = client.post("/evaluer", data={"profil": "particulier", "cas": "ecart_surface"})

    assert reponse.status_code == 200
    # Le lien vers l'autre profil doit porter le cas courant et viser /evaluer.
    assert "/evaluer?cas=ecart_surface&amp;profil=analyste" in reponse.text
    assert 'href="?profil=' not in reponse.text, (
        "Un lien de profil relatif subsiste : il produirait un GET sur la page courante."
    )

    disable_offline_guard()


@pytest.mark.regression
@pytest.mark.parametrize("chemin", ["/", "/transparence", "/exploitation"])
def test_bascule_de_profil_disponible_sur_toutes_les_pages(chemin: str) -> None:
    """Le meme defaut ne doit pas reapparaitre sur une autre page du parcours."""
    disable_offline_guard()

    with TestClient(app) as client:
        reponse = client.get(chemin, params={"profil": "particulier"})
        assert reponse.status_code == 200
        assert f"{chemin}?profil=analyste" in reponse.text

    disable_offline_guard()


def test_les_deux_profils_rendent_le_meme_calcul() -> None:
    """Le profil change la restitution, jamais le resultat.

    C'est la these du produit : deux lectures d'une meme evaluation. Deux
    utilisateurs obtenant des scores differents sur la meme donnee serait un
    defaut de conception, pas une fonctionnalite.
    """
    disable_offline_guard()

    with TestClient(app) as client:
        particulier = client.get("/evaluer", params={"profil": "particulier", "cas": "ecart_surface"})
        analyste = client.get("/evaluer", params={"profil": "analyste", "cas": "ecart_surface"})

    assert particulier.status_code == analyste.status_code == 200
    # Le motif metier est identique dans les deux lectures.
    assert "different de 45%" in particulier.text
    assert "different de 45%" in analyste.text
    # Seul l'analyste recoit la decomposition technique de l'ecart.
    assert "Décomposition de l'écart" in analyste.text
    assert "Décomposition de l'écart" not in particulier.text

    disable_offline_guard()
