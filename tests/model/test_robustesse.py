"""Mesures de robustesse du moteur Concorde. (projet de substitution n°21)"""

from __future__ import annotations

from copy import deepcopy
from datetime import date

import pandas as pd
import pytest
from api.model.schemas import RapprochementEntree
from app.exemples import charger

from concorde.clean.rapprochement import SORTIE
from concorde.features.construction import CHAMPS_SURVEILLES
from concorde.model.moteur import Moteur


@pytest.fixture(scope="module")
def moteur() -> Moteur:
    return Moteur.charger()


def test_perturbation_numerique_legere_ne_bascule_pas_plus_de_dix_pourcent(
    moteur: Moteur,
) -> None:
    """Detecte un seuil d'anomalie instable a un bruit de mesure de 1 %.

    Les dix premiers rapprochements apparies par identifiant sont une sonde
    deterministe. Une bascule sur au plus un cas (10 %) est tolerable car une
    observation exactement sur le seuil doit rester signalée comme incertaine.
    """
    table = pd.read_parquet(SORTIE).query("a_dpe").sort_values("id_rapprochement").head(10)
    bascules = 0
    for _, ligne in table.iterrows():
        reference = moteur.predire_un(ligne.to_dict())
        perturbe = ligne.to_dict()
        for champ in ("valeur_fonciere", "surface_reelle_bati", "surface_habitable_dpe", "conso_kwh_m2_an"):
            perturbe[champ] = float(perturbe[champ]) * 1.01
        resultat = moteur.predire_un(perturbe)
        bascules += resultat["niveau_anomalie"] != reference["niveau_anomalie"]

    assert bascules <= 1


@pytest.mark.parametrize("surface", [0.01, 2000.0])
@pytest.mark.parametrize("date_mutation", [date(2000, 1, 1), date(2100, 12, 31)])
def test_bornes_du_contrat_restent_evaluables(surface: float, date_mutation: date, moteur: Moteur) -> None:
    """Detecte une valeur de contrat valide qui ferait tomber l'inference."""
    charge = deepcopy(charger()["coherent"]["donnees"])
    charge["surface_reelle_bati"] = surface
    charge["date_mutation"] = date_mutation.isoformat()
    entree = RapprochementEntree.model_validate(charge)

    resultat = moteur.predire_un(entree.model_dump(mode="json"))

    assert resultat["statut"] == "evalue"


@pytest.mark.parametrize("champ", sorted(set(CHAMPS_SURVEILLES) - {"etiquette_dpe"}))
def test_absence_d_un_champ_optionnel_surveille_degrade_la_confiance(champ: str, moteur: Moteur) -> None:
    """Detecte un moteur qui masque un champ DPE manquant au lieu de le signaler."""
    charge = deepcopy(charger()["coherent"]["donnees"])
    reference = moteur.predire_un(charge)
    charge.pop(champ)

    # Le moteur est servi derriere le contrat Pydantic : un optionnel omis est
    # materialise en ``None`` avant l'inference, pas supprime du schema tabulaire.
    resultat = moteur.predire_un(RapprochementEntree.model_validate(charge).model_dump(mode="json"))

    assert resultat["confiance"]["score"] < reference["confiance"]["score"]


def test_etiquette_dpe_absente_est_refusee_par_le_contrat_avant_l_inference() -> None:
    """Detecte un DPE incomplet qui atteindrait le moteur en contournant le contrat."""
    charge = deepcopy(charger()["coherent"]["donnees"])
    charge.pop("etiquette_dpe")

    with pytest.raises(ValueError, match="etiquette_dpe"):
        RapprochementEntree.model_validate(charge)


def test_prediction_est_deterministe_a_entree_identique(moteur: Moteur) -> None:
    """Detecte une inference non deterministe sur un artefact pourtant gele."""
    charge = charger()["ecart_surface"]["donnees"]

    assert moteur.predire_un(charge) == moteur.predire_un(charge)


def test_absence_artefact_est_un_refus_explicite(tmp_path, moteur: Moteur) -> None:
    """Detecte une degradation silencieuse quand l'artefact de production manque."""
    with pytest.raises(FileNotFoundError, match="Artefact de modèle introuvable"):
        Moteur.charger(tmp_path / "inexistant.pt")
