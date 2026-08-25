"""Entrainement, evaluation et gel de l'artefact. (C12, C13)

    python -m concorde.model.entrainement

Enchainement : lecture de la table des rapprochements -> decoupage
entrainement / validation / test -> entrainement de l'auto-encodeur ->
calibration -> evaluation -> journalisation MLflow -> ecriture de l'artefact
et de la fiche de modele.

**Precaution methodologique assumee.** Le jeu de demonstration porte des
anomalies plantees, et les regles de coherence ont ete ecrites pour les memes
familles de contradictions. Le rappel des regles est donc circulaire : il mesure
la coherence du generateur avec lui-meme, pas une performance. La metrique
informative est le pouvoir de tri de l'auto-encodeur seul, qui n'a jamais vu les
regles ni les etiquettes. Les deux sont publiees, avec cette reserve inscrite
dans la fiche du modele.
"""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    precision_recall_fscore_support,
    roc_auc_score,
)

from concorde.clean.rapprochement import SORTIE as TABLE_RAPPROCHEMENTS
from concorde.collect.base import sha256_fichier
from concorde.common.logging_setup import new_request_id, setup_logging
from concorde.common.paths import DATA_SAMPLES, DOCS_DIR, PROJECT_ROOT, ensure_dirs
from concorde.features.construction import (
    VARIABLES_COMPARAISON,
    calculer_references,
    construire_variables,
    matrice_modele,
)
from concorde.model import regles_coherence
from concorde.model.autoencodeur import GRAINE, entrainer, erreurs
from concorde.model.moteur import SEUIL_ATYPIQUE, FicheModele, Moteur

log = setup_logging("train")

VERSION_MODELE = "0.1.0"
FICHE_MD = DOCS_DIR / "fiche-modele.md"
METRIQUES_JSON = PROJECT_ROOT / "reports" / "annexes" / "metriques_modele.json"


def _commit_git() -> str:
    try:
        return subprocess.check_output(  # noqa: S603
            ["git", "rev-parse", "--short", "HEAD"],  # noqa: S607
            cwd=PROJECT_ROOT, text=True, stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "inconnu"


def _decouper(df: pd.DataFrame, graine: int = GRAINE) -> dict[str, pd.DataFrame]:
    """Decoupe par `id_mutation` : une mutation ne peut pas etre a la fois
    dans l'entrainement et dans le test, meme si elle porte plusieurs DPE."""
    rng = np.random.default_rng(graine)
    mutations = df["id_mutation"].drop_duplicates().to_numpy()
    rng.shuffle(mutations)
    n = len(mutations)
    bornes = (int(n * 0.70), int(n * 0.85))
    parts = {
        "train": set(mutations[: bornes[0]]),
        "val": set(mutations[bornes[0]: bornes[1]]),
        "test": set(mutations[bornes[1]:]),
    }
    return {nom: df[df["id_mutation"].isin(ids)].copy() for nom, ids in parts.items()}


def _verite_terrain() -> pd.DataFrame:
    """Charge les anomalies plantees du jeu de demonstration, si elles existent."""
    chemin = DATA_SAMPLES / "verite_terrain.json"
    if not chemin.exists():
        return pd.DataFrame(columns=["id_mutation", "anormal"])
    brut = json.loads(chemin.read_text(encoding="utf-8"))
    return pd.DataFrame(
        [{"id_mutation": e["id_mutation"], "anormal": bool(e["anormal"])} for e in brut]
    )


def _motifs_majeurs(df: pd.DataFrame) -> np.ndarray:
    """Vrai lorsqu'au moins une règle de cohérence majeure se déclenche."""
    sortie = np.zeros(len(df), dtype=bool)
    for i, (_, ligne) in enumerate(df.iterrows()):
        _, motifs = regles_coherence.evaluer(ligne.to_dict())
        sortie[i] = any(m.gravite == "majeur" for m in motifs)
    return sortie


def entrainer_et_geler(
    table: Path | None = None, chemin_artefact: Path | None = None
) -> tuple[Moteur, dict[str, Any]]:
    ensure_dirs()
    new_request_id()

    chemin_table = table or TABLE_RAPPROCHEMENTS
    df = pd.read_parquet(chemin_table)
    empreinte = sha256_fichier(chemin_table)
    log.info(
        f"Table chargee : {len(df)} rapprochements",
        extra={"event": "chargement", "lignes": len(df), "empreinte": empreinte[:16]},
    )

    # Seuls les rapprochements apparies sont modelisables : on ne compare pas
    # une source a elle-meme.
    apparies = df[df["a_dpe"]].reset_index(drop=True)
    parts = _decouper(apparies)
    log.info(
        f"Decoupage : {len(parts['train'])} / {len(parts['val'])} / {len(parts['test'])}",
        extra={"event": "decoupage", "train": len(parts["train"]),
               "val": len(parts["val"]), "test": len(parts["test"])},
    )

    # Les references (medianes communales) sont calculees sur l'entrainement
    # seul : les calculer sur tout le jeu ferait fuir l'information du test.
    references = calculer_references(parts["train"])

    var_train = construire_variables(parts["train"], references)
    x_train, medianes = matrice_modele(var_train)
    var_val = construire_variables(parts["val"], references)
    x_val, _ = matrice_modele(var_val, medianes)

    moyennes = x_train.mean(axis=0)
    ecarts = x_train.std(axis=0)
    ecarts = np.where(ecarts == 0, 1.0, ecarts)
    xn_train = (x_train - moyennes) / ecarts
    xn_val = (x_val - moyennes) / ecarts

    modele, historique = entrainer(xn_train, xn_val)
    log.info(
        f"Entrainement termine : {len(historique.perte_entrainement)} epoques, "
        f"meilleure perte validation {historique.meilleure_perte_validation:.5f}",
        extra={"event": "entrainement", "epoques": len(historique.perte_entrainement),
               "perte_val": round(historique.meilleure_perte_validation, 6)},
    )

    grille = erreurs(modele, xn_train)

    table_aleas = (
        df.groupby("code_commune")[["alea_max", "nb_aleas_significatifs"]]
        .max()
        .astype(int)
        .to_dict(orient="index")
    )
    table_aleas = {str(k).zfill(5): {kk: int(vv) for kk, vv in v.items()}
                   for k, v in table_aleas.items()}

    fiche = FicheModele(
        version=VERSION_MODELE,
        entraine_le=datetime.now(UTC).isoformat(),
        graine=GRAINE,
        variables=list(VARIABLES_COMPARAISON),
        nb_lignes_entrainement=len(parts["train"]),
        nb_lignes_validation=len(parts["val"]),
        empreinte_donnees=empreinte,
        commit_git=_commit_git(),
    )

    moteur = Moteur(
        modele=modele,
        moyennes=moyennes,
        ecarts_types=ecarts,
        medianes_imputation=medianes,
        references=references,
        grille_calibration=grille,
        table_aleas=table_aleas,
        fiche=fiche,
    )

    metriques = _evaluer(moteur, parts, historique)
    fiche.metriques = {k: v for k, v in metriques.items() if isinstance(v, (int, float))}
    fiche.limites = [
        "Le detecteur est non supervise : aucune etiquette « rapprochement faux » n'existe "
        "dans les données publiques.",
        "Les règles de cohérence et les anomalies du jeu de démonstration relèvent des mêmes "
        "familles de contradictions : le rappel des règles est circulaire et n'est pas une "
        "mesure de performance.",
        "La base DPE de l'ADEME n'est pas representative du parc francais ; aucune "
        "generalisation a l'echelle nationale n'est possible.",
        "Le rapprochement s'appuie sur la parcelle cadastrale : il est ambigu en copropriete, "
        "ce que le système signale sans le résoudre.",
        "Le modèle ne prédit ni prix ni valeur : il qualifie la fiabilité d'un rapprochement.",
    ]

    chemin = moteur.sauvegarder(chemin_artefact)
    log.info(f"Artefact gele : {chemin}",
             extra={"event": "artefact", "chemin": str(chemin),
                    "octets": chemin.stat().st_size})

    _journaliser_mlflow(moteur, metriques, historique, chemin)
    _ecrire_fiche(moteur, metriques)

    METRIQUES_JSON.parent.mkdir(parents=True, exist_ok=True)
    METRIQUES_JSON.write_text(json.dumps(metriques, ensure_ascii=False, indent=2), encoding="utf-8")

    return moteur, metriques


def _evaluer(moteur: Moteur, parts: dict[str, pd.DataFrame], historique) -> dict[str, Any]:
    """Evalue sur le jeu de test, en separant ce qui est informatif de ce qui est circulaire."""
    test = parts["test"]
    resultat = moteur.predire_table(test)
    verite = _verite_terrain()

    metriques: dict[str, Any] = {
        "perte_validation": round(historique.meilleure_perte_validation, 6),
        "epoques_effectuees": len(historique.perte_entrainement),
        "nb_test": len(test),
        "taux_signalement_atypique": round(
            float((resultat["score_anomalie"] >= SEUIL_ATYPIQUE).mean()), 4
        ),
    }

    if verite.empty:
        metriques["evaluation_supervisee"] = "verite terrain absente"
        return metriques

    fusion = test[["id_mutation"]].merge(verite, on="id_mutation", how="left")
    y = fusion["anormal"].fillna(False).to_numpy().astype(int)
    scores = resultat["score_anomalie"].to_numpy()
    valides = ~np.isnan(scores)

    if y[valides].sum() > 0 and y[valides].sum() < valides.sum():
        # INFORMATIF : l'auto-encodeur n'a jamais vu ni les regles ni les etiquettes.
        metriques["auc_autoencodeur"] = round(
            float(roc_auc_score(y[valides], scores[valides])), 4
        )
        metriques["average_precision_autoencodeur"] = round(
            float(average_precision_score(y[valides], scores[valides])), 4
        )
        metriques["taux_base_anomalies"] = round(float(y[valides].mean()), 4)

        # CIRCULAIRE : publie pour transparence, sans valeur de performance.
        alerte_regles = _motifs_majeurs(resultat)
        p, r, f1, _ = precision_recall_fscore_support(
            y[valides], alerte_regles[valides].astype(int), average="binary", zero_division=0
        )
        metriques["regles_precision_circulaire"] = round(float(p), 4)
        metriques["regles_rappel_circulaire"] = round(float(r), 4)
        metriques["regles_f1_circulaire"] = round(float(f1), 4)

        # Systeme complet tel qu'il alerte en production.
        alerte = alerte_regles | (scores >= SEUIL_ATYPIQUE)
        p2, r2, f2, _ = precision_recall_fscore_support(
            y[valides], alerte[valides].astype(int), average="binary", zero_division=0
        )
        metriques["systeme_precision"] = round(float(p2), 4)
        metriques["systeme_rappel"] = round(float(r2), 4)
        metriques["systeme_f1"] = round(float(f2), 4)

    log.info(
        "Evaluation terminee",
        extra={"event": "evaluation", **{k: v for k, v in metriques.items()
                                         if isinstance(v, (int, float))}},
    )
    return metriques


def _journaliser_mlflow(moteur: Moteur, metriques: dict, historique, artefact: Path) -> None:
    """Journalise l'execution dans MLflow, magasin SQLite local (hors ligne).

    MLflow 3 a place le magasin fichier (`./mlruns`) en maintenance et refuse de
    l'ouvrir. Le backend SQLite reste entierement local — un fichier
    `mlflow.db` a la racine, aucun serveur, aucun reseau — tout en donnant acces
    au registre de modeles et aux comparaisons d'executions.
    """
    import mlflow

    mlflow.set_tracking_uri(f"sqlite:///{PROJECT_ROOT / 'mlflow.db'}")
    mlflow.set_experiment("concorde-moteur-confiance")
    with mlflow.start_run(run_name=f"v{VERSION_MODELE}-{moteur.fiche.commit_git}"):
        mlflow.log_params({
            "version": VERSION_MODELE,
            "graine": GRAINE,
            "variables": len(VARIABLES_COMPARAISON),
            "dim_cachee": moteur.modele.encodeur[0].out_features,
            "dim_latente": moteur.modele.encodeur[2].out_features,
            "lignes_entrainement": moteur.fiche.nb_lignes_entrainement,
            "empreinte_donnees": moteur.fiche.empreinte_donnees[:16],
            "commit_git": moteur.fiche.commit_git,
        })
        mlflow.log_metrics({k: float(v) for k, v in metriques.items()
                            if isinstance(v, (int, float))})
        for i, (pt, pv) in enumerate(
            zip(historique.perte_entrainement, historique.perte_validation, strict=True)
        ):
            mlflow.log_metric("perte_entrainement", pt, step=i)
            mlflow.log_metric("perte_validation", pv, step=i)
        mlflow.log_artifact(str(artefact), artifact_path="modele")
    log.info("Execution journalisee dans MLflow", extra={"event": "mlflow"})


def _ecrire_fiche(moteur: Moteur, metriques: dict) -> None:
    f = moteur.fiche
    lignes = [
        "# Fiche du modele — Concorde, moteur de confiance",
        "",
        "Document genere par `python -m concorde.model.entrainement`. Ne pas editer a la main.",
        "",
        "## Identite",
        "",
        "| Champ | Valeur |",
        "|---|---|",
        f"| Version | `{f.version}` |",
        f"| Entraine le | {f.entraine_le} |",
        f"| Commit Git | `{f.commit_git}` |",
        f"| Graine aleatoire | `{f.graine}` |",
        f"| Empreinte du jeu d'entrainement | `{f.empreinte_donnees[:32]}...` |",
        f"| Lignes d'entrainement / validation | {f.nb_lignes_entrainement} / "
        f"{f.nb_lignes_validation} |",
        "",
        "## Objet",
        "",
        "Le modele **ne predit ni prix ni valeur**. Il qualifie la fiabilite d'un rapprochement "
        "entre une mutation DVF+ et un DPE ADEME, sur trois axes independants : coherence "
        "(regles metier explicites), anomalie (auto-encodeur non supervise), confiance "
        "(completude et precision de l'information disponible).",
        "",
        "## Variables soumises au detecteur",
        "",
        *[f"- `{v}`" for v in f.variables],
        "",
        "## Metriques (jeu de test)",
        "",
        "| Metrique | Valeur | Lecture |",
        "|---|---:|---|",
    ]
    lectures = {
        "auc_autoencodeur": "**Informatif.** Pouvoir de tri de l'auto-encodeur seul, qui n'a "
                            "vu ni les regles ni les etiquettes.",
        "average_precision_autoencodeur": "**Informatif.** Précision moyenne, robuste au "
                                          "desequilibre des classes.",
        "taux_base_anomalies": "Proportion d'anomalies dans le jeu de test (reference).",
        "regles_precision_circulaire": "**Circulaire.** Les regles visent les memes familles "
                                       "de contradictions que celles plantees.",
        "regles_rappel_circulaire": "**Circulaire.** A ne pas presenter comme une performance.",
        "regles_f1_circulaire": "**Circulaire.**",
        "systeme_precision": "Systeme complet tel qu'il alerte (regles majeures OU score "
                             ">= percentile 95).",
        "systeme_rappel": "Systeme complet.",
        "systeme_f1": "Systeme complet.",
        "perte_validation": "Erreur quadratique de reconstruction sur la validation.",
        "epoques_effectuees": "Arret anticipe sur la perte de validation.",
        "taux_signalement_atypique": "Part du jeu de test signalee comme atypique.",
        "nb_test": "Taille du jeu de test.",
    }
    for cle, valeur in metriques.items():
        if isinstance(valeur, (int, float)):
            lignes.append(f"| `{cle}` | {valeur} | {lectures.get(cle, '')} |")
    lignes += ["", "## Limites assumees", ""]
    lignes += [f"- {limite}" for limite in f.limites]
    lignes += [
        "",
        "## Reproduction",
        "",
        "```bash",
        "python scripts/make_sample_fixture.py",
        "python -m concorde.collect",
        "python -m concorde.clean",
        "python -m concorde.model.entrainement",
        "```",
        "",
        f"Artefact produit : `models/concorde_moteur.pt` (graine `{f.graine}`, "
        "resultat deterministe).",
    ]
    FICHE_MD.parent.mkdir(parents=True, exist_ok=True)
    FICHE_MD.write_text("\n".join(lignes), encoding="utf-8")


def main() -> int:
    moteur, metriques = entrainer_et_geler()
    log.info(
        "Entrainement complet",
        extra={"event": "fin", "version": moteur.fiche.version,
               "auc": metriques.get("auc_autoencodeur")},
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
