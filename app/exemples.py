"""Cas de demonstration selectionnes dans le jeu reel. (C10)

La demonstration ne doit pas dependre d'une saisie manuelle reussie du premier
coup devant un jury. Ces cas sont choisis **dans la table des rapprochements**
produite par la chaine, pas inventes : ils illustrent chacun un comportement
distinct du systeme.
"""

from __future__ import annotations

import math
from functools import lru_cache
from typing import Any

import pandas as pd

from concorde.clean.rapprochement import SORTIE as TABLE

#: Ce que chaque cas doit demontrer.
INTENTIONS: dict[str, str] = {
    "coherent": "Rapprochement coherent, confiance elevee",
    "ecart_surface": "Surfaces DVF et DPE incompatibles",
    "dpe_posterieur": "DPE etabli apres la mutation",
    "parcelle_ambigue": "Plusieurs DPE sur la meme parcelle",
    "sans_dpe": "Aucun DPE rapproche : le systeme ne conclut pas",
}


def _propre(valeur: Any) -> Any:
    if valeur is None or (isinstance(valeur, float) and math.isnan(valeur)):
        return None
    if isinstance(valeur, pd.Timestamp):
        return valeur.date().isoformat()
    return valeur


def _vers_entree(ligne: pd.Series) -> dict[str, Any]:
    """Convertit une ligne de la table en charge utile acceptee par l'API."""
    a_dpe = bool(ligne.get("a_dpe"))
    charge: dict[str, Any] = {
        "id_mutation": str(ligne["id_mutation"]),
        "date_mutation": _propre(ligne["date_mutation"]),
        "valeur_fonciere": float(ligne["valeur_fonciere"]),
        "surface_reelle_bati": float(ligne["surface_reelle_bati"]),
        "type_local": str(ligne["type_local"]),
        "code_commune": str(ligne["code_commune"]).zfill(5),
        "id_parcelle": str(ligne["id_parcelle"]),
        "nb_dpe_candidats": int(ligne.get("nb_dpe_candidats", 0)),
    }
    if a_dpe:
        charge |= {
            "numero_dpe": str(ligne["numero_dpe"]),
            "date_dpe": _propre(ligne["date_dpe"]),
            "etiquette_dpe": str(ligne["etiquette_dpe"]),
            "surface_habitable_dpe": _propre(ligne.get("surface_habitable_dpe")),
            "type_batiment_dpe": _propre(ligne.get("type_batiment_norm")),
            "annee_construction": (
                int(ligne["annee_construction"])
                if _propre(ligne.get("annee_construction")) is not None else None
            ),
            "score_ban": _propre(ligne.get("score_ban")),
            "conso_kwh_m2_an": _propre(ligne.get("conso_kwh_m2_an")),
        }
    return {k: v for k, v in charge.items() if v is not None}


@lru_cache(maxsize=1)
def charger() -> dict[str, dict[str, Any]]:
    """Selectionne un cas par intention, de maniere deterministe."""
    if not TABLE.exists():
        return {}
    df = pd.read_parquet(TABLE)
    apparies = df[df["a_dpe"]].copy()
    apparies["_ecart_surface"] = (
        apparies["surface_reelle_bati"] - apparies["surface_habitable_dpe"]
    ).abs() / apparies[["surface_reelle_bati", "surface_habitable_dpe"]].max(axis=1)
    apparies["_delta_j"] = (
        pd.to_datetime(apparies["date_mutation"]) - pd.to_datetime(apparies["date_dpe"])
    ).dt.days

    cas: dict[str, dict[str, Any]] = {}

    def premier(sous_ensemble: pd.DataFrame, cle: str) -> None:
        if not sous_ensemble.empty:
            ligne = sous_ensemble.sort_values("id_mutation").iloc[0]
            cas[cle] = {"intitule": INTENTIONS[cle], "donnees": _vers_entree(ligne)}

    premier(
        apparies[
            (apparies["_ecart_surface"] < 0.05)
            & (apparies["_delta_j"].between(30, 2000))
            & (apparies["score_ban"] >= 0.9)
            & (apparies["nb_dpe_candidats"] == 1)
            & apparies["annee_construction"].notna()
        ],
        "coherent",
    )
    premier(apparies[apparies["_ecart_surface"] > 0.45], "ecart_surface")
    premier(apparies[apparies["_delta_j"] < 0], "dpe_posterieur")
    premier(apparies[apparies["nb_dpe_candidats"] > 1], "parcelle_ambigue")
    premier(df[~df["a_dpe"]].assign(_ecart_surface=0, _delta_j=0), "sans_dpe")
    return cas
