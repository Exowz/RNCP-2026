"""Preuves C1 pour le service web et la page web, sans acces Internet."""

from concorde.collect.page_web import CollecteurPageGeorisques
from concorde.collect.service_web import CollecteurBAN


def test_collecteur_ban_rejoue_une_reponse_api_capturee() -> None:
    """Detecte la disparition du cache local d'un service web requis en demo."""
    resultat = CollecteurBAN().collecter(mode="samples")

    assert resultat.succes
    assert resultat.type_source == "service_web"
    assert resultat.nb_lignes == 3


def test_collecteur_page_georisques_extrait_un_snapshot_html() -> None:
    """Detecte un scraper qui ne saurait plus rejouer sa page capturee localement."""
    resultat = CollecteurPageGeorisques().collecter(mode="samples")

    assert resultat.succes
    assert resultat.type_source == "page_web"
    assert resultat.nb_lignes == 2
