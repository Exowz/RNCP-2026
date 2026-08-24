"""Rapport Evidently hors ligne des derives de variables. (C11)"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset

from concorde.clean.rapprochement import SORTIE

COLONNES_SUIVIES = [
    "surface_reelle_bati",
    "surface_habitable_dpe",
    "valeur_fonciere",
    "score_ban",
    "conso_kwh_m2_an",
    "annee_construction",
]


def generer_rapport_derives(sortie: Path, table: Path = SORTIE) -> dict[str, int]:
    """Compare reference et lot courant, puis ecrit HTML/JSON Evidently."""
    df = pd.read_parquet(table)
    suivi = df[df["a_dpe"]][COLONNES_SUIVIES].dropna().reset_index(drop=True)
    borne = int(len(suivi) * 0.70)
    reference, courant = suivi.iloc[:borne], suivi.iloc[borne:]
    rapport = Report(metrics=[DataDriftPreset(columns=COLONNES_SUIVIES)])
    instantane = rapport.run(reference_data=reference, current_data=courant)
    sortie.mkdir(parents=True, exist_ok=True)
    instantane.save_html(str(sortie / "evidently_drift.html"))
    instantane.save_json(str(sortie / "evidently_drift.json"))
    return {"reference_lignes": len(reference), "courant_lignes": len(courant)}
