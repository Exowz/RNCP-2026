"""Construction des variables du moteur de confiance.

Trois familles de variables, volontairement separees parce qu'elles repondent a
trois questions differentes :

1. **Variables de comparaison** — mesurent l'accord entre les deux
   enregistrements rapproches (surface, type, chronologie, prix au m2 relatif
   a la commune). Ce sont elles qui alimentent le detecteur d'anomalie.
2. **Variables de contexte** — situent le bien (exposition aux aleas,
   anciennete, consommation). Elles enrichissent la description sans decider.
3. **Variables d'incertitude** — mesurent ce que l'on ne sait pas (champs
   manquants, precision du geocodage, nombre de DPE candidats sur la parcelle).
   Elles n'alimentent **pas** le detecteur d'anomalie : melanger « les donnees
   se contredisent » et « la donnee manque » produirait un score ininterpretable.

Regle d'exclusion assumee : un rapprochement sans DPE n'est pas score. Il sort en
`non_evaluable`. On ne peut pas mesurer un desaccord entre deux sources quand une
seule est presente.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

#: Variables soumises au detecteur d'anomalie, dans cet ordre. L'ordre fait
#: partie du contrat du modele : il est reinscrit dans l'artefact entraine.
VARIABLES_COMPARAISON: tuple[str, ...] = (
    "ecart_surface_rel",
    "ecart_temporel_annees",
    "dpe_posterieur_mutation",
    "desaccord_type_local",
    "log_prix_m2",
    "ecart_prix_m2_commune",
    "anciennete_bati",
    "conso_kwh_m2_an",
)

#: Variables qui alimentent le niveau de confiance, pas le score d'anomalie.
VARIABLES_INCERTITUDE: tuple[str, ...] = (
    "score_ban",
    "nb_dpe_candidats",
    "nb_champs_manquants",
)

#: Champs dont l'absence degrade la confiance, avec leur poids.
CHAMPS_SURVEILLES: dict[str, float] = {
    "surface_habitable_dpe": 1.0,
    "annee_construction": 0.5,
    "conso_kwh_m2_an": 0.5,
    "score_ban": 0.5,
    "etiquette_dpe": 1.0,
}


@dataclass(frozen=True, slots=True)
class ReferencesCommunales:
    """Medianes de prix au m2 par commune, calculees sur le jeu d'entrainement.

    Elles sont figees avec le modele : recalculer la mediane a l'inference
    laisserait la donnee de production influencer la reference, ce qui est une
    fuite et rendrait le score non reproductible.
    """

    medianes: dict[str, float]
    mediane_globale: float

    def mediane(self, code_commune: str) -> float:
        return self.medianes.get(str(code_commune), self.mediane_globale)


def calculer_references(df: pd.DataFrame) -> ReferencesCommunales:
    """Calcule les medianes de prix au m2, a figer avec le modele."""
    prix_m2 = df["valeur_fonciere"] / df["surface_reelle_bati"]
    valides = prix_m2[(prix_m2 > 100) & (prix_m2 < 30000)]
    par_commune = (
        pd.DataFrame({"code_commune": df.loc[valides.index, "code_commune"], "prix_m2": valides})
        .groupby("code_commune")["prix_m2"]
        .median()
    )
    return ReferencesCommunales(
        medianes={str(k): float(v) for k, v in par_commune.items()},
        mediane_globale=float(valides.median()),
    )


def construire_variables(
    df: pd.DataFrame, references: ReferencesCommunales
) -> pd.DataFrame:
    """Calcule toutes les variables sur la table des rapprochements.

    Renvoie une table indexee comme `df`, contenant les variables de comparaison,
    d'incertitude et les colonnes de restitution utiles a l'application.
    """
    out = pd.DataFrame(index=df.index)

    surf_dvf = pd.to_numeric(df["surface_reelle_bati"], errors="coerce")
    surf_dpe = pd.to_numeric(df.get("surface_habitable_dpe"), errors="coerce")
    valeur = pd.to_numeric(df["valeur_fonciere"], errors="coerce")

    # --- 1. Variables de comparaison ---
    denominateur = pd.concat([surf_dvf, surf_dpe], axis=1).max(axis=1)
    out["ecart_surface_rel"] = ((surf_dvf - surf_dpe).abs() / denominateur).clip(0, 3)

    date_mut = pd.to_datetime(df["date_mutation"], errors="coerce")
    date_dpe = pd.to_datetime(df.get("date_dpe"), errors="coerce")
    delta_jours = (date_mut - date_dpe).dt.days
    out["ecart_temporel_annees"] = (delta_jours.abs() / 365.25).clip(0, 25)
    out["dpe_posterieur_mutation"] = (delta_jours < 0).astype(float)

    type_dvf = df["type_local_norm"].astype(str)
    type_dpe = df.get("type_batiment_norm", pd.Series(index=df.index, dtype=object)).astype(str)
    connu = type_dpe.notna() & (type_dpe != "nan") & (type_dpe != "")
    out["desaccord_type_local"] = ((type_dvf != type_dpe) & connu).astype(float)

    prix_m2 = (valeur / surf_dvf).replace([np.inf, -np.inf], np.nan)
    out["log_prix_m2"] = np.log1p(prix_m2.clip(lower=0))
    ref = df["code_commune"].astype(str).map(references.mediane).astype(float)
    out["ecart_prix_m2_commune"] = ((prix_m2 - ref) / ref).clip(-1, 10)

    annee = pd.to_numeric(df.get("annee_construction"), errors="coerce")
    out["anciennete_bati"] = (date_mut.dt.year - annee).clip(0, 250)

    out["conso_kwh_m2_an"] = pd.to_numeric(df.get("conso_kwh_m2_an"), errors="coerce").clip(0, 1500)

    # --- 2. Variables d'incertitude ---
    out["score_ban"] = pd.to_numeric(df.get("score_ban"), errors="coerce")
    out["nb_dpe_candidats"] = pd.to_numeric(df["nb_dpe_candidats"], errors="coerce").fillna(0)

    manquants = pd.Series(0.0, index=df.index)
    for champ, poids in CHAMPS_SURVEILLES.items():
        if champ in df.columns:
            manquants = manquants + df[champ].isna().astype(float) * poids
        else:
            manquants = manquants + poids
    out["nb_champs_manquants"] = manquants

    # --- 3. Colonnes de restitution (jamais soumises au modele) ---
    out["prix_m2"] = prix_m2
    out["a_dpe"] = df["a_dpe"].astype(bool)
    out["alea_max"] = pd.to_numeric(df["alea_max"], errors="coerce").fillna(0)
    out["nb_aleas_significatifs"] = pd.to_numeric(
        df["nb_aleas_significatifs"], errors="coerce"
    ).fillna(0)

    return out


def matrice_modele(
    variables: pd.DataFrame, medianes_imputation: dict[str, float] | None = None
) -> tuple[np.ndarray, dict[str, float]]:
    """Extrait la matrice numerique soumise au modele, valeurs manquantes imputees.

    L'imputation utilise les medianes du jeu d'entrainement, figees dans
    l'artefact. Recalculer une mediane a l'inference ferait dependre le score
    d'un lot de prediction, ce qui interdirait toute reproductibilite.
    """
    bloc = variables.loc[:, list(VARIABLES_COMPARAISON)].astype(float)
    if medianes_imputation is None:
        medianes_imputation = {c: float(bloc[c].median()) for c in bloc.columns}
        medianes_imputation = {
            c: (0.0 if not np.isfinite(v) else v) for c, v in medianes_imputation.items()
        }
    for colonne in bloc.columns:
        bloc[colonne] = bloc[colonne].fillna(medianes_imputation[colonne])
    return bloc.to_numpy(dtype=np.float32), medianes_imputation
