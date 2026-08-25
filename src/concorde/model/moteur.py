"""Artefact de modele gele et moteur d'inference. (C9, C13)

L'artefact (`models/concorde_moteur.pt`) contient **tout** ce qui est necessaire
pour rejouer une prediction a l'identique :

- les poids de l'auto-encodeur ;
- les parametres de normalisation (moyennes, ecarts-types) ;
- les medianes d'imputation ;
- les medianes de prix communales de reference ;
- la grille de calibration qui transforme une erreur de reconstruction en
  percentile ;
- la table d'exposition aux aleas ;
- une fiche : version, date, graine, empreinte du jeu d'entrainement, metriques.

Consequence : servir le modele ne demande **aucun** acces reseau, aucune base,
aucun recalcul sur les donnees de production. C'est ce qui rend la demonstration
hors ligne possible et la prediction reproductible.

Le meme code de variables sert a l'entrainement et a l'inference
(`features.construction`). Il ne peut donc pas exister d'ecart entre ce que le
modele a appris et ce qu'on lui presente en production.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch

from concorde.common.paths import MODELS_DIR
from concorde.features.construction import (
    VARIABLES_COMPARAISON,
    ReferencesCommunales,
    construire_variables,
    matrice_modele,
)
from concorde.model import confiance as mod_confiance
from concorde.model import regles_coherence
from concorde.model.autoencodeur import AutoEncodeur, erreurs, erreurs_par_variable

CHEMIN_ARTEFACT_DEFAUT = MODELS_DIR / "concorde_moteur.pt"

#: Seuils de qualification du score d'anomalie (percentile d'entrainement).
SEUIL_ATYPIQUE = 0.95
SEUIL_A_VERIFIER = 0.80


@dataclass(slots=True)
class FicheModele:
    """Carte d'identite du modele, exposee par l'API et affichee dans l'application."""

    version: str
    entraine_le: str
    graine: int
    variables: list[str]
    nb_lignes_entrainement: int
    nb_lignes_validation: int
    empreinte_donnees: str
    commit_git: str
    metriques: dict[str, float] = field(default_factory=dict)
    limites: list[str] = field(default_factory=list)

    def en_dict(self) -> dict[str, Any]:
        return asdict(self)


class Moteur:
    """Charge un artefact gele et produit des verdicts."""

    def __init__(
        self,
        modele: AutoEncodeur,
        moyennes: np.ndarray,
        ecarts_types: np.ndarray,
        medianes_imputation: dict[str, float],
        references: ReferencesCommunales,
        grille_calibration: np.ndarray,
        table_aleas: dict[str, dict[str, int]],
        fiche: FicheModele,
    ) -> None:
        self.modele = modele
        self.moyennes = moyennes
        self.ecarts_types = np.where(ecarts_types == 0, 1.0, ecarts_types)
        self.medianes_imputation = medianes_imputation
        self.references = references
        self.grille_calibration = np.sort(grille_calibration)
        self.table_aleas = table_aleas
        self.fiche = fiche

    # ---------------------------------------------------------------- calcul

    def _normaliser(self, x: np.ndarray) -> np.ndarray:
        return (x - self.moyennes) / self.ecarts_types

    def percentile(self, erreur: float | np.ndarray) -> np.ndarray:
        """Transforme une erreur de reconstruction en percentile d'entrainement."""
        rang = np.searchsorted(self.grille_calibration, erreur, side="right")
        return np.asarray(rang / max(len(self.grille_calibration), 1), dtype=float)

    @staticmethod
    def qualifier(score: float) -> str:
        if score >= SEUIL_ATYPIQUE:
            return "atypique"
        if score >= SEUIL_A_VERIFIER:
            return "a_verifier"
        return "normal"

    def enrichir_aleas(self, code_commune: str) -> dict[str, int]:
        """Complete l'exposition aux aleas depuis la table figee dans l'artefact."""
        return self.table_aleas.get(
            str(code_commune).zfill(5), {"alea_max": 0, "nb_aleas_significatifs": 0}
        )

    # ------------------------------------------------------------ inference

    def predire_table(self, rapprochements: pd.DataFrame) -> pd.DataFrame:
        """Score une table entiere de rapprochements (entrainement, evaluation, lots)."""
        variables = construire_variables(rapprochements, self.references)
        x, _ = matrice_modele(variables, self.medianes_imputation)
        xn = self._normaliser(x)

        err = erreurs(self.modele, xn)
        err_par_var = erreurs_par_variable(self.modele, xn)
        scores = self.percentile(err)

        resultat = variables.copy()
        resultat["erreur_reconstruction"] = err
        resultat["score_anomalie"] = scores
        resultat["niveau_anomalie"] = [self.qualifier(float(s)) for s in scores]
        for i, nom in enumerate(VARIABLES_COMPARAISON):
            resultat[f"contrib__{nom}"] = err_par_var[:, i]
        # Un rapprochement sans DPE n'est pas score : on ne compare pas une
        # source a elle-meme.
        sans_dpe = ~resultat["a_dpe"].astype(bool)
        resultat.loc[sans_dpe, ["score_anomalie", "erreur_reconstruction"]] = np.nan
        resultat.loc[sans_dpe, "niveau_anomalie"] = "non_evaluable"
        return resultat

    def predire_un(self, enregistrement: dict[str, Any]) -> dict[str, Any]:
        """Score un rapprochement unique et renvoie un verdict complet et lisible."""
        ligne = dict(enregistrement)
        exposition = self.enrichir_aleas(ligne.get("code_commune", ""))
        ligne.setdefault("alea_max", exposition["alea_max"])
        ligne.setdefault("nb_aleas_significatifs", exposition["nb_aleas_significatifs"])
        ligne.setdefault("nb_dpe_candidats", 1)
        ligne["a_dpe"] = bool(ligne.get("numero_dpe"))
        ligne["type_local_norm"] = str(ligne.get("type_local", "")).strip().lower()
        ligne["type_batiment_norm"] = str(ligne.get("type_batiment_dpe", "")).strip().lower()

        df = pd.DataFrame([ligne])
        variables = construire_variables(df, self.references)
        v = variables.iloc[0].to_dict()

        a_dpe = bool(ligne["a_dpe"])
        if a_dpe:
            score_coherence, motifs = regles_coherence.evaluer(v)
        else:
            score_coherence, motifs = None, []
        conf = mod_confiance.evaluer(v, a_dpe=a_dpe)

        verdict: dict[str, Any] = {
            "id_mutation": ligne.get("id_mutation"),
            "numero_dpe": ligne.get("numero_dpe"),
            "statut": "evalue" if a_dpe else "non_evaluable",
            "score_anomalie": None,
            "niveau_anomalie": "non_evaluable",
            "score_coherence": None if score_coherence is None else round(float(score_coherence), 3),
            "motifs": [m.en_dict() for m in motifs],
            "confiance": conf.en_dict(),
            "exposition_aleas": {
                "niveau_max": int(ligne["alea_max"]),
                "nb_aleas_significatifs": int(ligne["nb_aleas_significatifs"]),
            },
            "variables_atypiques": [],
            "modele": {"version": self.fiche.version, "entraine_le": self.fiche.entraine_le},
        }

        if not a_dpe:
            verdict["explication"] = (
                "Aucun DPE n'a pu etre rapproche de cette mutation. Le systeme ne produit "
                "pas de score : il signale une inconnue."
            )
            return verdict

        x, _ = matrice_modele(variables, self.medianes_imputation)
        xn = self._normaliser(x)
        err_par_var = erreurs_par_variable(self.modele, xn)[0]
        score = float(self.percentile(float(err_par_var.mean())))

        verdict["score_anomalie"] = round(score, 3)
        verdict["niveau_anomalie"] = self.qualifier(score)
        verdict["erreur_reconstruction"] = round(float(err_par_var.mean()), 6)
        # Les trois variables qui contribuent le plus a l'ecart : c'est la
        # reponse a « pourquoi cette ligne est-elle signalee ? ».
        ordre = np.argsort(err_par_var)[::-1][:3]
        total = float(err_par_var.sum()) or 1.0
        verdict["variables_atypiques"] = [
            {
                "variable": VARIABLES_COMPARAISON[i],
                "part_de_l_ecart": round(float(err_par_var[i] / total), 3),
                "valeur": None if pd.isna(v.get(VARIABLES_COMPARAISON[i]))
                else round(float(v[VARIABLES_COMPARAISON[i]]), 4),
            }
            for i in ordre
        ]
        verdict["explication"] = _rediger_explication(verdict)
        return verdict

    # ------------------------------------------------------- serialisation

    def sauvegarder(self, chemin: Path | None = None) -> Path:
        chemin = chemin or CHEMIN_ARTEFACT_DEFAUT
        chemin.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "format": 1,
                "poids": self.modele.state_dict(),
                "dim_entree": self.modele.dim_entree,
                "architecture": {
                    "dim_cachee": self.modele.encodeur[0].out_features,
                    "dim_latente": self.modele.encodeur[2].out_features,
                },
                "moyennes": self.moyennes.tolist(),
                "ecarts_types": self.ecarts_types.tolist(),
                "medianes_imputation": self.medianes_imputation,
                "references_medianes": self.references.medianes,
                "references_globale": self.references.mediane_globale,
                "grille_calibration": self.grille_calibration.tolist(),
                "table_aleas": self.table_aleas,
                "fiche": self.fiche.en_dict(),
                "variables": list(VARIABLES_COMPARAISON),
            },
            chemin,
        )
        return chemin

    @classmethod
    def charger(cls, chemin: Path | None = None) -> Moteur:
        chemin = chemin or CHEMIN_ARTEFACT_DEFAUT
        if not chemin.exists():
            raise FileNotFoundError(
                f"Artefact de modele introuvable : {chemin}. "
                "Executer `python -m concorde.model.entrainement` pour le produire."
            )
        # L'artefact Concorde ne contient que tenseurs et types primitifs ; ne jamais
        # deserialiser du code Python arbitraire depuis un fichier modele.
        # Compatibilite avec l'artefact local produit avant le format 1.1 : les
        # seuls objets historiques autorises sont les tableaux NumPy de donnees.
        # Aucun callable applicatif n'est autorise par cette liste fermee.
        numpy_historiques = [
            np._core.multiarray._reconstruct,
            np.ndarray,
            np.dtype,
            type(np.dtype(np.float32)),
            type(np.dtype(np.float64)),
        ]
        with torch.serialization.safe_globals(numpy_historiques):
            etat = torch.load(chemin, map_location="cpu", weights_only=True)

        variables_artefact = tuple(etat["variables"])
        if variables_artefact != VARIABLES_COMPARAISON:
            raise ValueError(
                "Le contrat de variables de l'artefact ne correspond pas au code courant.\n"
                f"  artefact : {variables_artefact}\n  code     : {VARIABLES_COMPARAISON}\n"
                "Reentrainer le modele avant de le servir."
            )

        modele = AutoEncodeur(
            etat["dim_entree"],
            dim_cachee=etat["architecture"]["dim_cachee"],
            dim_latente=etat["architecture"]["dim_latente"],
        )
        modele.load_state_dict(etat["poids"])
        modele.eval()

        return cls(
            modele=modele,
            moyennes=np.asarray(etat["moyennes"], dtype=np.float32),
            ecarts_types=np.asarray(etat["ecarts_types"], dtype=np.float32),
            medianes_imputation=etat["medianes_imputation"],
            references=ReferencesCommunales(
                medianes=etat["references_medianes"],
                mediane_globale=etat["references_globale"],
            ),
            grille_calibration=np.asarray(etat["grille_calibration"], dtype=np.float64),
            table_aleas=etat["table_aleas"],
            fiche=FicheModele(**etat["fiche"]),
        )


def _rediger_explication(verdict: dict[str, Any]) -> str:
    """Redige une phrase destinee a l'utilisateur, pas au data scientist."""
    niveau = verdict["niveau_anomalie"]
    coherence = verdict["score_coherence"]
    motifs = verdict["motifs"]
    conf = verdict["confiance"]["niveau"]

    if motifs:
        majeurs = [m for m in motifs if m["gravite"] == "majeur"]
        tete = (
            f"{len(majeurs)} contradiction(s) majeure(s) detectee(s) entre la mutation et le DPE."
            if majeurs
            else f"{len(motifs)} reserve(s) de coherence detectee(s)."
        )
    elif niveau == "atypique":
        tete = (
            "Aucune contradiction connue, mais ce rapprochement ne ressemble pas au reste "
            "du jeu de donnees."
        )
    else:
        tete = "Aucune contradiction detectee entre la mutation et le DPE."

    queue = {
        "eleve": "Les donnees disponibles permettent de le dire avec un bon niveau de certitude.",
        "moyen": "Des informations manquent : lire ce resultat avec prudence.",
        "faible": "Trop d'informations manquent pour se fier a ce resultat.",
        "insuffisant": "Les donnees ne permettent pas de conclure.",
    }[conf]
    return f"{tete} Coherence : {coherence:.0%}. {queue}"
