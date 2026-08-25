"""Nettoyage, homogeneisation et rapprochement multi-sources. (C3)

Trois jeux entrent (`data/raw/`), un seul sort (`data/processed/`) : la table des
**rapprochements candidats**, unite d'analyse de tout le systeme.

Le rapprochement se fait sur `id_parcelle`. Ce choix est discutable et c'est le
sujet du projet : la parcelle cadastrale est le seul identifiant partage par DVF+
et par l'adressage BAN porte par les DPE. Il est fiable quand une parcelle porte
un seul logement, ambigu des qu'elle en porte plusieurs (copropriete). Le systeme
n'efface pas cette ambiguite : il la compte (`nb_dpe_candidats`) et la fait
redescendre dans le score de confiance.

Les mutations sans DPE rapprochable sont **conservees**, pas jetees : l'absence
d'information est une information, et c'est precisement ce que l'application doit
dire a l'utilisateur.
"""

from __future__ import annotations

import json

import pandas as pd

from concorde.clean.regles import RapportNettoyage, Regle, appliquer
from concorde.common.logging_setup import setup_logging
from concorde.common.paths import DATA_PROCESSED, DATA_RAW, REPORTS_DIR

log = setup_logging("clean")

SORTIE = DATA_PROCESSED / "rapprochements.parquet"
RAPPORT_JSON = REPORTS_DIR / "annexes" / "nettoyage_avant_apres.json"
RAPPORT_MD = REPORTS_DIR / "annexes" / "nettoyage_avant_apres.md"

#: Correspondance noms officiels ADEME -> noms internes normalises.
RENOMMAGE_DPE: dict[str, str] = {
    "N°DPE": "numero_dpe",
    "Date_établissement_DPE": "date_dpe",
    "Etiquette_DPE": "etiquette_dpe",
    "Etiquette_GES": "etiquette_ges",
    "Surface_habitable_logement": "surface_habitable_dpe",
    "Type_bâtiment": "type_batiment_dpe",
    "Année_construction": "annee_construction",
    "Adresse_(BAN)": "adresse_ban",
    "Code_postal_(BAN)": "code_postal_ban",
    "Code_INSEE_(BAN)": "code_commune_ban",
    "Identifiant__BAN": "identifiant_ban",
    "Score_BAN": "score_ban",
    "Conso_5_usages_par_m²_é_primaire": "conso_kwh_m2_an",
    "Emission_GES_5_usages_par_m²": "ges_kg_m2_an",
    "Coordonnée_cartographique_X_(BAN)": "lon_ban",
    "Coordonnée_cartographique_Y_(BAN)": "lat_ban",
    "id_parcelle_rapprochee": "id_parcelle",
}

#: Ordre des niveaux d'alea Georisques, du plus faible au plus fort.
ECHELLE_ALEA: dict[str, int] = {
    "nul": 0, "tres faible": 1, "faible": 2, "modere": 3, "moyen": 3, "fort": 4,
}

# --------------------------------------------------------------------------- #
# Regles DVF
# --------------------------------------------------------------------------- #

REGLES_DVF: list[Regle] = [
    Regle(
        "DVF-01", "surface batie exploitable",
        "Une surface nulle, absente ou negative rend tout ratio au m2 indefini : "
        "la ligne ne peut ni etre comparee ni etre rapprochee.",
        lambda d: d[d["surface_reelle_bati"].notna() & (d["surface_reelle_bati"] > 0)],
    ),
    Regle(
        "DVF-02", "surface batie plausible (<= 2000 m2)",
        "Au-dela de 2000 m2 il ne s'agit plus d'un logement mais d'un lot ou d'une "
        "saisie erronee ; le perimetre du projet est le logement.",
        lambda d: d[d["surface_reelle_bati"] <= 2000],
    ),
    Regle(
        "DVF-03", "valeur fonciere renseignee et positive",
        "La valeur fonciere sert de signal de coherence (pas de prediction). "
        "Absente ou nulle, elle ne porte aucune information exploitable.",
        lambda d: d[d["valeur_fonciere"].notna() & (d["valeur_fonciere"] > 0)],
    ),
    Regle(
        "DVF-04", "type de local retenu (Maison ou Appartement)",
        "Les dependances et locaux industriels n'ont pas de DPE logement "
        "comparable : les rapprocher produirait du bruit, pas de l'information.",
        lambda d: d[d["type_local"].isin(["Maison", "Appartement"])],
    ),
    Regle(
        "DVF-05", "deduplication (id_mutation, id_parcelle)",
        "Une mutation portant plusieurs dispositions apparait plusieurs fois dans "
        "DVF+ ; sans deduplication, le meme bien pese plusieurs fois dans les scores.",
        lambda d: d.drop_duplicates(subset=["id_mutation", "id_parcelle"], keep="first"),
    ),
    Regle(
        "DVF-06", "date de mutation valide",
        "Une date non interpretable interdit de calculer l'ecart temporel avec le "
        "DPE, qui est un signal de coherence central.",
        lambda d: d[pd.to_datetime(d["date_mutation"], errors="coerce").notna()],
    ),
]

# --------------------------------------------------------------------------- #
# Regles DPE
# --------------------------------------------------------------------------- #

REGLES_DPE: list[Regle] = [
    Regle(
        "DPE-01", "numero de DPE present",
        "Le numero ADEME est la cle de reference du diagnostic : sans lui, "
        "l'enregistrement n'est pas verifiable a la source.",
        lambda d: d[d["numero_dpe"].notna() & (d["numero_dpe"].astype(str).str.len() > 0)],
    ),
    Regle(
        "DPE-02", "etiquette dans l'echelle reglementaire A-G",
        "Toute autre valeur signale un enregistrement corrompu ou hors norme.",
        lambda d: d[d["etiquette_dpe"].isin(list("ABCDEFG"))],
    ),
    Regle(
        "DPE-03", "date d'etablissement valide",
        "Necessaire pour situer le diagnostic par rapport a la mutation.",
        lambda d: d[pd.to_datetime(d["date_dpe"], errors="coerce").notna()],
    ),
    Regle(
        "DPE-04", "deduplication par numero de DPE",
        "Les exports ADEME successifs peuvent republier un meme diagnostic.",
        lambda d: d.drop_duplicates(subset=["numero_dpe"], keep="last"),
    ),
]


def _normaliser_dvf(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["code_commune"] = d["code_commune"].astype(str).str.zfill(5)
    d["date_mutation"] = pd.to_datetime(d["date_mutation"], errors="coerce")
    d["surface_reelle_bati"] = pd.to_numeric(d["surface_reelle_bati"], errors="coerce")
    d["valeur_fonciere"] = pd.to_numeric(d["valeur_fonciere"], errors="coerce")
    # Homogeneisation du vocabulaire : DVF ecrit "Appartement", l'ADEME "appartement".
    d["type_local_norm"] = d["type_local"].astype(str).str.strip().str.lower()
    return d


def _normaliser_dpe(df: pd.DataFrame) -> pd.DataFrame:
    d = df.rename(columns=RENOMMAGE_DPE).copy()
    d["code_commune_ban"] = d["code_commune_ban"].astype(str).str.zfill(5)
    d["date_dpe"] = pd.to_datetime(d["date_dpe"], errors="coerce")
    for col in ("surface_habitable_dpe", "annee_construction", "score_ban",
                "conso_kwh_m2_an", "ges_kg_m2_an"):
        d[col] = pd.to_numeric(d[col], errors="coerce")
    d["type_batiment_norm"] = d["type_batiment_dpe"].astype(str).str.strip().str.lower()
    return d


def _normaliser_aleas(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["code_commune"] = d["code_commune"].astype(str).str.zfill(5)
    d["niveau_alea_num"] = (
        d["niveau_alea"].astype(str).str.strip().str.lower().map(ECHELLE_ALEA).fillna(0)
    )
    # Une ligne par commune : niveau maximal et nombre d'aleas significatifs.
    agrege = d.groupby("code_commune").agg(
        alea_max=("niveau_alea_num", "max"),
        nb_aleas_significatifs=("niveau_alea_num", lambda s: int((s >= 3).sum())),
    ).reset_index()
    return agrege


def construire(
    dvf: pd.DataFrame | None = None,
    dpe: pd.DataFrame | None = None,
    aleas: pd.DataFrame | None = None,
    ecrire: bool = True,
) -> tuple[pd.DataFrame, list[RapportNettoyage]]:
    """Nettoie, homogeneise et rapproche les trois sources.

    Returns:
        La table des rapprochements candidats et les rapports de nettoyage.
    """
    dvf = dvf if dvf is not None else pd.read_parquet(DATA_RAW / "dvf.parquet")
    dpe = dpe if dpe is not None else pd.read_parquet(DATA_RAW / "dpe.parquet")
    aleas = aleas if aleas is not None else pd.read_parquet(DATA_RAW / "aleas.parquet")

    dvf_n, rapport_dvf = appliquer(_normaliser_dvf(dvf), REGLES_DVF, "dvf")
    dpe_n, rapport_dpe = appliquer(_normaliser_dpe(dpe), REGLES_DPE, "dpe")
    aleas_n = _normaliser_aleas(aleas)

    log.info(
        "Nettoyage termine",
        extra={"event": "nettoyage", "dvf_avant": rapport_dvf.lignes_initiales,
               "dvf_apres": rapport_dvf.lignes_finales,
               "dpe_avant": rapport_dpe.lignes_initiales,
               "dpe_apres": rapport_dpe.lignes_finales},
    )

    # Nombre de DPE candidats par parcelle : mesure directe de l'ambiguite du
    # rapprochement, conservee comme variable et non masquee.
    candidats = dpe_n.groupby("id_parcelle").size().rename("nb_dpe_candidats").reset_index()

    # Jointure a gauche : une mutation sans DPE reste dans la table.
    rappr = dvf_n.merge(dpe_n, on="id_parcelle", how="left", suffixes=("", "_dpe"))
    rappr = rappr.merge(candidats, on="id_parcelle", how="left")
    rappr["nb_dpe_candidats"] = rappr["nb_dpe_candidats"].fillna(0).astype(int)
    rappr = rappr.merge(aleas_n, on="code_commune", how="left")
    rappr["alea_max"] = rappr["alea_max"].fillna(0).astype(int)
    rappr["nb_aleas_significatifs"] = rappr["nb_aleas_significatifs"].fillna(0).astype(int)

    rappr["a_dpe"] = rappr["numero_dpe"].notna()
    rappr["id_rapprochement"] = (
        rappr["id_mutation"].astype(str) + "|" + rappr["numero_dpe"].fillna("SANS_DPE").astype(str)
    )

    taux_appariement = float(rappr["a_dpe"].mean())
    log.info(
        f"Rapprochement : {len(rappr)} candidats, taux d'appariement {taux_appariement:.1%}",
        extra={"event": "rapprochement", "nb_rapprochements": len(rappr),
               "taux_appariement": round(taux_appariement, 4),
               "nb_sans_dpe": int((~rappr["a_dpe"]).sum())},
    )

    if ecrire:
        DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
        rappr.to_parquet(SORTIE, index=False)
        _ecrire_rapports([rapport_dvf, rapport_dpe], rappr, taux_appariement)
        log.info(f"Table ecrite : {SORTIE}", extra={"event": "ecriture",
                                                    "chemin": str(SORTIE), "lignes": len(rappr)})

    return rappr, [rapport_dvf, rapport_dpe]


def _ecrire_rapports(
    rapports: list[RapportNettoyage], rappr: pd.DataFrame, taux: float
) -> None:
    RAPPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    charge = {
        "rapports_nettoyage": [r.en_dict() for r in rapports],
        "rapprochement": {
            "nb_rapprochements": len(rappr),
            "nb_avec_dpe": int(rappr["a_dpe"].sum()),
            "nb_sans_dpe": int((~rappr["a_dpe"]).sum()),
            "taux_appariement": round(taux, 6),
            "parcelles_multi_dpe": int((rappr["nb_dpe_candidats"] > 1).sum()),
        },
    }
    RAPPORT_JSON.write_text(json.dumps(charge, ensure_ascii=False, indent=2), encoding="utf-8")

    md = ["# Nettoyage et rapprochement — tableau avant / apres", "",
          "Généré par `python -m concorde.clean`. Ne pas éditer à la main.", ""]
    md += [r.en_markdown() + "\n" for r in rapports]
    md += [
        "### Rapprochement DVF+ x DPE",
        "",
        "| Indicateur | Valeur |",
        "|---|---:|",
        f"| Rapprochements candidats | {len(rappr)} |",
        f"| Avec DPE apparie | {int(rappr['a_dpe'].sum())} |",
        f"| Sans DPE (inconnue assumee) | {int((~rappr['a_dpe']).sum())} |",
        f"| Taux d'appariement | {taux:.2%} |",
        f"| Parcelles portant plusieurs DPE (ambiguite) | "
        f"{int((rappr['nb_dpe_candidats'] > 1).sum())} |",
    ]
    RAPPORT_MD.write_text("\n".join(md), encoding="utf-8")
