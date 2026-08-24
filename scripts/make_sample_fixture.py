"""Genere les fixtures de la demonstration hors ligne.

Pourquoi une fixture plutot que les donnees reelles pour la tranche verticale ?

- La demonstration doit tourner sans Internet et les tests doivent etre
  deterministes : une fixture a graine fixe garantit les deux.
- Elle porte **les noms de colonnes reels** de DVF+ (Cerema/DGALN) et de
  l'Observatoire DPE-Audit (ADEME). Brancher les extractions reelles est donc
  un changement de source, pas une reecriture du nettoyage.
- Elle contient des anomalies **plantees et documentees** (ecarts de surface,
  DPE posterieur a la mutation, champs manquants, geocodage grossier), ce qui
  rend le comportement du moteur verifiable ligne a ligne.

Les donnees reelles collectees en ligne atterrissent dans `data/raw/` ; ces
fixtures vivent dans `data/samples/` et sont versionnees dans Git.

Usage :
    python scripts/make_sample_fixture.py
"""

from __future__ import annotations

import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 20260824
SAMPLES = Path(__file__).resolve().parents[1] / "data" / "samples"

# Trois communes contrastees : une metropole dense, une ville moyenne,
# une commune rurale exposee au retrait-gonflement des argiles.
COMMUNES = [
    {"code_commune": "33063", "nom_commune": "BORDEAUX", "code_postal": "33000",
     "code_departement": "33", "lat": 44.8378, "lon": -0.5792, "prix_m2_median": 4600},
    {"code_commune": "17300", "nom_commune": "ROCHEFORT", "code_postal": "17300",
     "code_departement": "17", "lat": 45.9414, "lon": -0.9628, "prix_m2_median": 2350},
    {"code_commune": "24016", "nom_commune": "ANNESSE-ET-BEAULIEU", "code_postal": "24430",
     "code_departement": "24", "lat": 45.0870, "lon": 0.5570, "prix_m2_median": 1650},
]

VOIES = [
    ("RUE", "SAINTE CATHERINE"), ("COURS", "DE L ARGONNE"), ("AVENUE", "THIERS"),
    ("RUE", "DU PALAIS"), ("PLACE", "COLBERT"), ("ROUTE", "DE PERIGUEUX"),
    ("IMPASSE", "DES VIGNES"), ("ALLEE", "DES CHENES"), ("RUE", "GAMBETTA"),
]

ETIQUETTES = ["A", "B", "C", "D", "E", "F", "G"]
# Distribution volontairement biaisee vers D-E-F : la base DPE n'est pas
# representative du parc, l'ADEME demande une lecture prudente.
POIDS_ETIQUETTES = [2, 6, 14, 27, 24, 17, 10]


def _voie(rng: random.Random) -> tuple[str, str]:
    return rng.choice(VOIES)


def generer(nb_biens: int = 900) -> dict[str, list[dict]]:
    rng = random.Random(SEED)
    dvf: list[dict] = []
    dpe: list[dict] = []
    aleas: list[dict] = []
    verite: list[dict] = []  # anomalies plantees, pour verifier le moteur

    for i in range(nb_biens):
        commune = rng.choice(COMMUNES)
        type_voie, nom_voie = _voie(rng)
        numero = rng.randint(1, 180)
        parcelle = f"{commune['code_commune']}000{rng.choice('ABCDEZ')}{rng.randint(1, 999):04d}"

        appartement = rng.random() < 0.55
        type_local = "Appartement" if appartement else "Maison"
        code_type_local = "2" if appartement else "1"
        surface = rng.randint(28, 95) if appartement else rng.randint(70, 210)
        pieces = max(1, round(surface / rng.uniform(20, 32)))
        annee_construction = rng.choice(
            [1890, 1930, 1962, 1975, 1983, 1994, 2003, 2011, 2019]
        )

        date_mutation = date(2023, 1, 1) + timedelta(days=rng.randint(0, 900))
        prix_m2 = commune["prix_m2_median"] * rng.uniform(0.72, 1.34)
        valeur_fonciere = round(prix_m2 * surface, 2)

        # --- Perturbations plantees, tracees dans la verite terrain ---
        # On distingue deux natures qui ne doivent jamais etre confondues :
        #   - une ANOMALIE : les deux enregistrements se contredisent ;
        #   - une INCERTITUDE : l'information manque ou est imprecise.
        # Un geocodage grossier n'est pas une anomalie, c'est une inconnue.
        anomalies: list[str] = []
        incertitudes: list[str] = []
        surface_dpe = float(surface)
        date_dpe = date_mutation - timedelta(days=rng.randint(5, 900))
        type_batiment = "appartement" if appartement else "maison"

        r = rng.random()
        if r < 0.06:  # ecart de surface important : rapprochement douteux
            surface_dpe = round(surface * rng.uniform(1.45, 2.3), 1)
            anomalies.append("ecart_surface")
        elif r < 0.10:  # DPE etabli apres la mutation
            date_dpe = date_mutation + timedelta(days=rng.randint(20, 400))
            anomalies.append("dpe_posterieur_mutation")
        elif r < 0.13:  # desaccord sur le type de bien
            type_batiment = "maison" if appartement else "appartement"
            anomalies.append("desaccord_type_local")
        elif r < 0.17:  # valeur fonciere aberrante (vente en viager, lot complexe)
            valeur_fonciere = round(valeur_fonciere * rng.choice([0.08, 0.12, 7.5]), 2)
            anomalies.append("valeur_fonciere_atypique")

        dvf.append({
            "id_mutation": f"2023-{i + 100000}",
            "date_mutation": date_mutation.isoformat(),
            "numero_disposition": "1",
            "nature_mutation": "Vente",
            "valeur_fonciere": valeur_fonciere,
            "adresse_numero": numero,
            "adresse_suffixe": "",
            "adresse_nom_voie": f"{type_voie} {nom_voie}",
            "code_postal": commune["code_postal"],
            "code_commune": commune["code_commune"],
            "nom_commune": commune["nom_commune"],
            "code_departement": commune["code_departement"],
            "id_parcelle": parcelle,
            "nombre_lots": rng.choice([0, 0, 0, 1, 2]),
            "code_type_local": code_type_local,
            "type_local": type_local,
            "surface_reelle_bati": surface,
            "nombre_pieces_principales": pieces,
            "surface_terrain": "" if appartement else rng.randint(120, 2400),
            "longitude": round(commune["lon"] + rng.uniform(-0.05, 0.05), 6),
            "latitude": round(commune["lat"] + rng.uniform(-0.04, 0.04), 6),
        })

        # 78 % des mutations ont un DPE rapprochable : le reste est une inconnue
        # assumee, pas un bug. C'est exactement ce que le produit doit rendre visible.
        if rng.random() < 0.78:
            etiquette = rng.choices(ETIQUETTES, weights=POIDS_ETIQUETTES, k=1)[0]
            conso = {"A": 60, "B": 90, "C": 140, "D": 200, "E": 280,
                     "F": 360, "G": 460}[etiquette] * rng.uniform(0.85, 1.15)
            score_ban = rng.choices(
                [0.98, 0.95, 0.92, 0.88, 0.71, 0.55], weights=[24, 26, 22, 16, 8, 4], k=1
            )[0]
            if score_ban < 0.75:
                incertitudes.append("geocodage_incertain")

            ligne_dpe = {
                "N°DPE": f"23{commune['code_departement']}E{i:07d}",
                "Date_établissement_DPE": date_dpe.isoformat(),
                "Etiquette_DPE": etiquette,
                "Etiquette_GES": rng.choices(ETIQUETTES, weights=POIDS_ETIQUETTES, k=1)[0],
                "Surface_habitable_logement": surface_dpe,
                "Type_bâtiment": type_batiment,
                "Année_construction": annee_construction,
                "Adresse_(BAN)": f"{numero} {type_voie} {nom_voie} {commune['code_postal']} "
                                 f"{commune['nom_commune']}",
                "Code_postal_(BAN)": commune["code_postal"],
                "Code_INSEE_(BAN)": commune["code_commune"],
                "Identifiant__BAN": f"{commune['code_commune']}_{rng.randint(1000, 9999)}_{numero:05d}",
                "Score_BAN": score_ban,
                "Conso_5_usages_par_m²_é_primaire": round(conso, 1),
                "Emission_GES_5_usages_par_m²": round(conso * rng.uniform(0.02, 0.09), 2),
                "Coordonnée_cartographique_X_(BAN)": round(commune["lon"], 6),
                "Coordonnée_cartographique_Y_(BAN)": round(commune["lat"], 6),
                "id_parcelle_rapprochee": parcelle,
            }
            # Champs manquants : la base ADEME en comporte reellement.
            if rng.random() < 0.09:
                ligne_dpe["Année_construction"] = ""
                incertitudes.append("annee_construction_manquante")
            if rng.random() < 0.05:
                ligne_dpe["Surface_habitable_logement"] = ""
                incertitudes.append("surface_dpe_manquante")
            dpe.append(ligne_dpe)

        verite.append({
            "id_mutation": f"2023-{i + 100000}",
            "anomalies_plantees": anomalies,
            "incertitudes_plantees": incertitudes,
            "anormal": bool(anomalies),
        })

    # --- Georisques : exposition par commune (extrait du service web) ---
    for commune in COMMUNES:
        rng_c = random.Random(SEED + int(commune["code_commune"]))
        catalogue = [
            ("inondation", rng_c.choice(["Faible", "Moyen", "Fort"])),
            ("retrait_gonflement_argiles", rng_c.choice(["Faible", "Moyen", "Fort"])),
            ("cavites_souterraines", rng_c.choice(["Nul", "Faible", "Moyen"])),
            ("seisme", rng_c.choice(["Tres faible", "Faible", "Modere"])),
        ]
        for libelle, niveau in catalogue:
            aleas.append({
                "code_commune": commune["code_commune"],
                "nom_commune": commune["nom_commune"],
                "type_alea": libelle,
                "niveau_alea": niveau,
                "source": "Georisques (BRGM) - extrait fige pour demonstration hors ligne",
            })

    ajouter_lignes_corrompues(dvf, dpe, random.Random(SEED + 7))

    return {"dvf": dvf, "dpe": dpe, "aleas": aleas, "verite": verite}



def ajouter_lignes_corrompues(dvf: list[dict], dpe: list[dict], rng: random.Random) -> None:
    """Injecte les defauts que porte reellement la donnee publique.

    Sans eux, les regles de nettoyage passeraient sur un jeu deja propre et le
    tableau avant/apres de C3 serait vide : les regles seraient ecrites, mais
    pas prouvees. Chaque defaut injecte correspond a une regle nommee.
    """
    modele = dict(dvf[0])
    n = len(dvf)

    # DVF-01 : surface batie nulle ou absente (frequent sur les terrains nus).
    for i in range(int(n * 0.025)):
        ligne = dict(rng.choice(dvf))
        ligne["id_mutation"] = f"2023-COR-S{i}"
        ligne["surface_reelle_bati"] = rng.choice([0, "", -12])
        dvf.append(ligne)

    # DVF-02 : surface aberrante (lot entier saisi comme un logement).
    for i in range(int(n * 0.008)):
        ligne = dict(rng.choice(dvf))
        ligne["id_mutation"] = f"2023-COR-XL{i}"
        ligne["surface_reelle_bati"] = rng.randint(2400, 9800)
        dvf.append(ligne)

    # DVF-03 : valeur fonciere absente (mutation a titre gratuit, echange).
    for i in range(int(n * 0.02)):
        ligne = dict(rng.choice(dvf))
        ligne["id_mutation"] = f"2023-COR-V{i}"
        ligne["valeur_fonciere"] = ""
        dvf.append(ligne)

    # DVF-04 : types de local hors perimetre logement.
    for i in range(int(n * 0.03)):
        ligne = dict(rng.choice(dvf))
        ligne["id_mutation"] = f"2023-COR-T{i}"
        ligne["type_local"] = rng.choice(["Dependance", "Local industriel. commercial ou assimile"])
        ligne["code_type_local"] = rng.choice(["3", "4"])
        dvf.append(ligne)

    # DVF-05 : mutations a dispositions multiples -> doublons stricts.
    for ligne in rng.sample(dvf[:n], int(n * 0.02)):
        double = dict(ligne)
        double["numero_disposition"] = "2"
        dvf.append(double)

    # DVF-06 : date non interpretable (export tronque).
    for i in range(int(n * 0.006)):
        ligne = dict(rng.choice(dvf))
        ligne["id_mutation"] = f"2023-COR-D{i}"
        ligne["date_mutation"] = rng.choice(["0000-00-00", "n/a", ""])
        dvf.append(ligne)

    rng.shuffle(dvf)
    del modele

    m = len(dpe)
    # DPE-01 : numero de diagnostic absent.
    for i in range(int(m * 0.015)):
        ligne = dict(rng.choice(dpe))
        ligne["N\u00b0DPE"] = ""
        dpe.append(ligne)

    # DPE-02 : etiquette hors echelle reglementaire.
    for i in range(int(m * 0.012)):
        ligne = dict(rng.choice(dpe))
        ligne["N\u00b0DPE"] = f"COR-ET{i}"
        ligne["Etiquette_DPE"] = rng.choice(["N", "-", "?"])
        dpe.append(ligne)

    # DPE-03 : date d'etablissement invalide.
    for i in range(int(m * 0.01)):
        ligne = dict(rng.choice(dpe))
        ligne["N\u00b0DPE"] = f"COR-DT{i}"
        ligne["Date_\u00e9tablissement_DPE"] = rng.choice(["", "0001-01-01x"])
        dpe.append(ligne)

    # DPE-04 : republication d'un meme diagnostic dans deux exports.
    for ligne in rng.sample(dpe[:m], int(m * 0.02)):
        dpe.append(dict(ligne))

    rng.shuffle(dpe)


def ecrire(donnees: dict[str, list[dict]]) -> None:
    SAMPLES.mkdir(parents=True, exist_ok=True)

    for nom, lignes, fichier in (
        ("dvf", donnees["dvf"], "dvf_sample.csv"),
        ("dpe", donnees["dpe"], "dpe_ademe_sample.csv"),
        ("aleas", donnees["aleas"], "georisques_sample.csv"),
    ):
        chemin = SAMPLES / fichier
        with chemin.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(lignes[0].keys()))
            writer.writeheader()
            writer.writerows(lignes)
        print(f"  {chemin.relative_to(SAMPLES.parents[1])} : {len(lignes)} lignes")

    verite = SAMPLES / "verite_terrain.json"
    verite.write_text(
        json.dumps(donnees["verite"], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    total = len(donnees["verite"])
    nb_anormaux = sum(1 for v in donnees["verite"] if v["anormal"])
    nb_incertains = sum(1 for v in donnees["verite"] if v["incertitudes_plantees"])
    print(f"  {verite.relative_to(SAMPLES.parents[1])} : {total} rapprochements, "
          f"{nb_anormaux} avec anomalie plantee ({nb_anormaux / total:.1%}), "
          f"{nb_incertains} avec incertitude plantee ({nb_incertains / total:.1%})")


if __name__ == "__main__":
    print(f"Generation des fixtures (graine={SEED}) :")
    ecrire(generer())
