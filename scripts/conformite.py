#!/usr/bin/env python3
"""Produit la porte de conformité qualité, robustesse et sécurité.

Le script est volontairement autonome : il constitue une preuve exécutable avant
la construction du paquet et laisse, à chaque passage, un rapport consultable
hors ligne dans ``reports/annexes``.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
RAPPORT_JSON = RACINE / "reports" / "annexes" / "conformite.json"
RAPPORT_MARKDOWN = RACINE / "reports" / "annexes" / "conformite.md"
DERNIER_AUDIT_PIP = RACINE / "reports" / "annexes" / "pip-audit-dernier-succes.json"
METRIQUES_MODELE = RACINE / "reports" / "annexes" / "metriques_modele.json"
EXCEPTION_DISKCACHE = "PYSEC-2026-2447"

class Verdict(StrEnum):
    """Les trois états possibles, y compris l'incertitude hors ligne."""

    CONFORME = "conforme"
    NON_CONFORME = "non conforme"
    NON_EVALUE = "non évalué"


@dataclass(frozen=True)
class Critere:
    """Une mesure indépendante de la porte de conformité."""

    identifiant: str
    axe: str
    libelle: str
    seuil: str
    valeur_mesuree: str
    verdict: Verdict
    justification_seuil: str
    bloquant: bool = True


def executer(*commande: str) -> subprocess.CompletedProcess[str]:
    """Exécute un contrôle sans masquer sa sortie à l'appelant."""

    return subprocess.run(  # noqa: S603 - commandes constantes définies dans cette porte, sans shell
        commande,
        cwd=RACINE,
        capture_output=True,
        text=True,
        check=False,
    )


#: Ligne de bilan de pytest (« 3 passed in 0.42s »), plus informative que la
#: ligne de progression qui la precede et que l'on ramassait auparavant.
_BILAN_PYTEST = re.compile(r"^\d+ (passed|failed|error)", re.MULTILINE)


def resume_sortie(resultat: subprocess.CompletedProcess[str]) -> str:
    """Resume l'execution d'un controle en une valeur lisible par un humain.

    Prendre betement la derniere ligne de sortie donnait, pour pytest, la ligne
    de points de progression (« ...... [100%] ») : le tableau de conformite
    affichait alors du bruit de terminal la ou le jury attend une mesure. On
    cherche donc d'abord la ligne de bilan, et l'on ne retombe sur la derniere
    ligne qu'a defaut.
    """
    sortie = (resultat.stdout + resultat.stderr).strip()
    if not sortie:
        return f"code retour {resultat.returncode}, aucune sortie"
    bilan = _BILAN_PYTEST.search(sortie)
    if bilan:
        return bilan.group(0).replace("passed", "test(s) reussi(s)").replace(
            "failed", "test(s) en echec").replace("error", "erreur(s)")
    derniere = sortie.splitlines()[-1].strip()
    return f"code retour {resultat.returncode} — {derniere[:90]}"


def critere_commande(
    identifiant: str,
    axe: str,
    libelle: str,
    seuil: str,
    justification: str,
    *commande: str,
) -> Critere:
    resultat = executer(*commande)
    return Critere(
        identifiant=identifiant,
        axe=axe,
        libelle=libelle,
        seuil=seuil,
        valeur_mesuree=resume_sortie(resultat),
        verdict=Verdict.CONFORME if resultat.returncode == 0 else Verdict.NON_CONFORME,
        justification_seuil=justification,
    )


def mesurer_couverture() -> Critere:
    resultat = executer(
        sys.executable,
        "-m",
        "pytest",
        "-m",
        "not local_service",
        "-q",
        "--cov=src/concorde",
        "--cov=api",
        "--cov=app",
        "--cov-report=term",
    )
    sortie = resultat.stdout + resultat.stderr
    correspondance = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", sortie)
    couverture = int(correspondance.group(1)) if correspondance else None
    conforme = resultat.returncode == 0 and couverture is not None and couverture >= 75
    valeur = f"{couverture}%" if couverture is not None else "couverture non lisible"
    return Critere(
        identifiant="qualite.couverture_tests",
        axe="qualité",
        libelle="Tests automatisés et couverture",
        seuil="suite verte et couverture >= 75 %",
        valeur_mesuree=valeur,
        verdict=Verdict.CONFORME if conforme else Verdict.NON_CONFORME,
        justification_seuil="75 % est le plancher annoncé pour le projet de substitution; la suite doit aussi rester verte.",
    )


def mesurer_auc() -> Critere:
    try:
        auc = float(json.loads(METRIQUES_MODELE.read_text(encoding="utf-8"))["auc_autoencodeur"])
    except (FileNotFoundError, KeyError, TypeError, ValueError, json.JSONDecodeError) as erreur:
        return Critere(
            "qualite.auc_autoencodeur",
            "qualité",
            "Pouvoir discriminant de l'autoencodeur",
            "AUC >= 0,80",
            f"métrique indisponible ({erreur})",
            Verdict.NON_CONFORME,
            "0,80 constitue le minimum documenté pour distinguer utilement les cas atypiques des cas ordinaires.",
        )
    return Critere(
        "qualite.auc_autoencodeur",
        "qualité",
        "Pouvoir discriminant de l'autoencodeur",
        "AUC >= 0,80",
        f"AUC {auc:.4f}",
        Verdict.CONFORME if auc >= 0.80 else Verdict.NON_CONFORME,
        "0,80 constitue le minimum documenté pour distinguer utilement les cas atypiques des cas ordinaires.",
    )


def mesurer_artefact() -> Critere:
    try:
        from concorde.features.construction import VARIABLES_COMPARAISON
        from concorde.model.moteur import CHEMIN_ARTEFACT_DEFAUT, Moteur

        moteur = Moteur.charger(CHEMIN_ARTEFACT_DEFAUT)
        contrat = tuple(moteur.fiche.variables) == tuple(VARIABLES_COMPARAISON)
        present = CHEMIN_ARTEFACT_DEFAUT.exists()
        conforme = present and contrat
        valeur = (
            f"présent ({CHEMIN_ARTEFACT_DEFAUT.name}), chargeable, "
            f"contrat {'conforme' if contrat else 'non conforme'}"
        )
    except Exception as erreur:  # la porte doit transformer toute erreur de chargement en verdict
        conforme = False
        valeur = f"artefact non vérifiable ({type(erreur).__name__}: {erreur})"
    return Critere(
        "qualite.artefact_et_contrat",
        "qualité",
        "Artefact PyTorch et contrat des variables",
        "artefact présent, chargeable et variables attendues à l'identique",
        valeur,
        Verdict.CONFORME if conforme else Verdict.NON_CONFORME,
        "Un modèle non chargeable ou dont les variables diffèrent ne peut pas produire une prédiction reproductible.",
    )


def mesurer_bandit() -> Critere:
    resultat = executer(
        sys.executable,
        "-m",
        "bandit",
        "-c",
        "pyproject.toml",
        "-r",
        "src",
        "api",
        "app",
        "-f",
        "json",
    )
    try:
        donnees = json.loads(resultat.stdout)
        resultats = donnees.get("results", [])
        hautes = sum(issue["issue_severity"] in {"HIGH", "MEDIUM"} for issue in resultats)
        valeur = f"{hautes} finding(s) HIGH/MEDIUM"
    except (json.JSONDecodeError, KeyError, TypeError):
        hautes = 1
        valeur = "rapport Bandit illisible"
    return Critere(
        "securite.bandit",
        "sécurité",
        "Analyse statique Bandit",
        "0 finding HIGH et 0 finding MEDIUM",
        valeur,
        Verdict.CONFORME if hautes == 0 else Verdict.NON_CONFORME,
        "Les sévérités HIGH et MEDIUM représentent un risque exploitable ou à traiter avant livraison; les LOW restent visibles dans le rapport Bandit.",
    )


def derniere_evaluation_pip() -> str:
    try:
        return str(json.loads(DERNIER_AUDIT_PIP.read_text(encoding="utf-8"))["date"])
    except (FileNotFoundError, KeyError, ValueError, json.JSONDecodeError):
        return "aucune"


def mesurer_pip_audit(hors_ligne: bool) -> Critere:
    if hors_ligne:
        return Critere(
            "securite.pip_audit",
            "sécurité",
            "Audit des dépendances Python",
            "0 vulnérabilité non acceptée",
            f"non évalué (hors ligne; dernière évaluation réussie: {derniere_evaluation_pip()})",
            Verdict.NON_EVALUE,
            "pip-audit consulte une base d'avis en ligne; hors ligne, la porte refuse de conclure à la conformité sans bloquer la démonstration.",
        )

    resultat = executer(sys.executable, "-m", "pip_audit", "--format", "json", "--ignore-vuln", EXCEPTION_DISKCACHE)
    try:
        rapport = json.loads(resultat.stdout)
        dependances = rapport.get("dependencies", []) if isinstance(rapport, dict) else rapport
        nombre = sum(len(paquet.get("vulns", [])) for paquet in dependances)
    except (json.JSONDecodeError, TypeError, AttributeError):
        nombre = 1
    if resultat.returncode == 0 and nombre == 0:
        DERNIER_AUDIT_PIP.parent.mkdir(parents=True, exist_ok=True)
        DERNIER_AUDIT_PIP.write_text(
            json.dumps(
                {
                    "date": datetime.now(UTC).isoformat(),
                    "commande": f"pip-audit --ignore-vuln {EXCEPTION_DISKCACHE}",
                    "exception_documentee": EXCEPTION_DISKCACHE,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    return Critere(
        "securite.pip_audit",
        "sécurité",
        "Audit des dépendances Python",
        "0 vulnérabilité non acceptée",
        f"{nombre} vulnérabilité non acceptée (exception documentée: {EXCEPTION_DISKCACHE})",
        Verdict.CONFORME if resultat.returncode == 0 and nombre == 0 else Verdict.NON_CONFORME,
        "L'avis sans correctif de diskcache est une exception temporaire et tracée dans docs/securite.md; toute autre vulnérabilité bloque la livraison.",
    )


def mesurer_secrets() -> Critere:
    resultat = executer("git", "ls-files")
    fichiers = resultat.stdout.splitlines()
    interdits = [
        chemin
        for chemin in fichiers
        if (
            Path(chemin).name in {".env", ".env.local"}
            or Path(chemin).suffix.lower() in {".pem", ".key"}
            or chemin.startswith("secrets/")
        )
        and not chemin.endswith(".env.example")
    ]
    return Critere(
        "securite.secrets_versionnes",
        "sécurité",
        "Absence de secret en clair versionné",
        "aucun .env réel, secret/, .pem ou .key suivi par Git",
        "aucun fichier sensible suivi" if not interdits else ", ".join(interdits),
        Verdict.CONFORME if not interdits else Verdict.NON_CONFORME,
        "Une clé versionnée reste récupérable même après révocation; les exemples sans secret réel restent autorisés.",
    )


def mesurer_authentification_et_entetes() -> list[Critere]:
    try:
        from api.model.main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        reponse = client.post("/predict", json={})
        sante = client.get("/sante")
        authentification = reponse.status_code == 401
        entetes_attendus = {
            "x-content-type-options",
            "x-frame-options",
            "referrer-policy",
            "content-security-policy",
        }
        entetes = entetes_attendus.issubset({cle.lower() for cle in sante.headers})
        valeur_auth = f"HTTP {reponse.status_code} sans clé"
        valeur_entetes = f"{len(entetes_attendus & {cle.lower() for cle in sante.headers})}/{len(entetes_attendus)} en-têtes attendus"
    except Exception as erreur:  # même si l'API locale est indisponible, le contrôle doit être honnête
        authentification = entetes = False
        valeur_auth = valeur_entetes = f"vérification impossible ({type(erreur).__name__}: {erreur})"
    return [
        Critere(
            "securite.401_sans_cle",
            "sécurité",
            "Refus sans clé d'API",
            "POST /predict sans X-API-Key retourne 401",
            valeur_auth,
            Verdict.CONFORME if authentification else Verdict.NON_CONFORME,
            "L'absence d'authentification ne doit jamais donner accès au moteur de prédiction.",
        ),
        Critere(
            "securite.entetes_owasp",
            "sécurité",
            "En-têtes HTTP de durcissement",
            "CSP, anti-clickjacking, nosniff et referrer policy présents",
            valeur_entetes,
            Verdict.CONFORME if entetes else Verdict.NON_CONFORME,
            "Ces quatre en-têtes couvrent les protections web minimales revendiquées par l'application.",
        ),
    ]


def mesurer_robustesse() -> list[Critere]:
    mesures = [
        (
            "robustesse.perturbation",
            "Stabilité, bornes et champs optionnels",
            "au plus 10 % de bascules sur 10 cas, bruit de 1 %; bornes et absences sans exception",
            "Un bruit de mesure réaliste ne doit pas modifier massivement une décision; les limites et absences doivent rester explicites et sûres.",
            "tests/model/test_robustesse.py",
        ),
        (
            "robustesse.determinisme",
            "Déterminisme de l'inférence",
            "deux appels identiques donnent exactement le même résultat",
            "Un score instable empêcherait toute analyse et toute reproductibilité de la décision.",
            "tests/model/test_robustesse.py::test_prediction_est_deterministe_a_entree_identique",
        ),
        (
            "robustesse.artefact_absent",
            "Refus propre d'un artefact manquant",
            "FileNotFoundError explicite, sans prédiction dégradée silencieuse",
            "Un moteur sans artefact ne doit jamais simuler un résultat ni échouer de façon ambiguë.",
            "tests/model/test_robustesse.py::test_absence_artefact_est_un_refus_explicite",
        ),
    ]
    return [
        critere_commande(
            identifiant,
            "robustesse",
            libelle,
            seuil,
            justification,
            sys.executable,
            "-m",
            "pytest",
            # Pas de `-q` ici : `addopts` en fournit deja un dans pyproject.toml,
            # et un second (`-qq`) supprime la ligne de bilan « N passed », qui
            # est precisement la mesure que le tableau doit afficher.
            test,
        )
        for identifiant, libelle, seuil, justification, test in mesures
    ]


def mesurer_chaine_entrainement() -> Critere:
    """Verifie que la chaine d'entrainement s'execute encore de bout en bout.

    Angle mort corrige le 25 aout 2026. La porte inspectait l'artefact — present,
    chargeable, contrat conforme — sans jamais rejouer la chaine qui le produit.
    Le remplacement de `mlflow` par `mlflow-skinny` a casse la journalisation
    MLflow (`ModuleNotFoundError: alembic`) : l'entrainement echouait, et la
    porte affichait pourtant « CONFORME », parce qu'un artefact valide restait
    sur le disque depuis le passage precedent.

    Un artefact valide ne prouve que le passe. Ce critere prouve le present.

    L'entrainement ecrit dans un repertoire temporaire : la porte ne doit jamais
    modifier l'artefact suivi par DVC, sous peine de rendre `dvc status` sale a
    chaque controle.
    """
    programme = (
        "import pathlib, tempfile;"
        "from concorde.model.entrainement import entrainer_et_geler;"
        "entrainer_et_geler("
        "chemin_artefact=pathlib.Path(tempfile.mkdtemp()) / 'controle.pt')"
    )
    resultat = executer(sys.executable, "-c", programme)
    return Critere(
        identifiant="qualite.chaine_entrainement",
        axe="qualite",
        libelle="Chaine d'entrainement rejouable",
        seuil="`entrainer_et_geler` s'execute sans erreur, journalisation MLflow comprise",
        valeur_mesuree=(
            "chaine rejouee sans erreur"
            if resultat.returncode == 0
            else resume_sortie(resultat)
        ),
        verdict=Verdict.CONFORME if resultat.returncode == 0 else Verdict.NON_CONFORME,
        justification_seuil=(
            "Un artefact valide sur le disque ne prouve pas que la chaine qui l'a produit "
            "fonctionne encore. Sans ce controle, une dependance retiree casse "
            "l'entrainement sans que la porte le voie."
        ),
    )


def mesurer_criteres(hors_ligne: bool) -> list[Critere]:
    """Calcule toutes les mesures qui composent la décision de livraison."""

    criteres = [mesurer_couverture(), mesurer_auc(), mesurer_artefact()]
    criteres.append(mesurer_chaine_entrainement())
    criteres.extend(mesurer_robustesse())
    criteres.extend([mesurer_bandit(), mesurer_pip_audit(hors_ligne), mesurer_secrets()])
    criteres.extend(mesurer_authentification_et_entetes())
    return criteres


def code_retour(criteres: list[Critere]) -> int:
    """Retourne 1 uniquement lorsqu'un contrôle bloquant est non conforme."""

    return int(any(critere.bloquant and critere.verdict == Verdict.NON_CONFORME for critere in criteres))


def rendu_markdown(criteres: list[Critere], date_generation: str) -> str:
    verdict_global = "CONFORME" if code_retour(criteres) == 0 else "NON CONFORME"
    lignes = [
        "# Tableau de conformité Secure MLOps",
        "",
        f"Généré le {date_generation}. Ce fichier est produit par `python scripts/conformite.py`; ne pas l'éditer à la main.",
        "",
        f"**Verdict global : {verdict_global}**",
        "",
        "| ID | Axe | Critère | Seuil | Valeur mesurée | Verdict | Justification du seuil |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for critere in criteres:
        lignes.append(
            "| {id} | {axe} | {libelle} | {seuil} | {valeur} | {verdict} | {justification} |".format(
                id=critere.identifiant,
                axe=critere.axe,
                libelle=critere.libelle,
                seuil=critere.seuil,
                valeur=critere.valeur_mesuree.replace("|", "/"),
                verdict=critere.verdict,
                justification=critere.justification_seuil,
            )
        )
    return "\n".join(lignes) + "\n"


# Nom français conservé comme alias public pour les tests et les lecteurs du script.
rendre_markdown = rendu_markdown


def ecrire_rapports(criteres: list[Critere]) -> None:
    """Persiste les deux formes du même verdict pour la soutenance hors ligne."""

    date_generation = datetime.now(UTC).isoformat()
    RAPPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    contenu_json = {
        "genere_le": date_generation,
        "verdict_global": Verdict.CONFORME if code_retour(criteres) == 0 else Verdict.NON_CONFORME,
        "criteres": [asdict(critere) for critere in criteres],
    }
    RAPPORT_JSON.write_text(json.dumps(contenu_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    RAPPORT_MARKDOWN.write_text(rendu_markdown(criteres, date_generation), encoding="utf-8")


def forcer_echec(criteres: list[Critere], identifiant: str | None) -> list[Critere]:
    if identifiant is None:
        return criteres
    remplaces = []
    trouve = False
    for critere in criteres:
        if critere.identifiant == identifiant:
            trouve = True
            remplaces.append(
                Critere(
                    **{
                        **asdict(critere),
                        "valeur_mesuree": "échec forcé pour vérification de la porte",
                        "verdict": Verdict.NON_CONFORME,
                    }
                )
            )
        else:
            remplaces.append(critere)
    if not trouve:
        raise ValueError(f"Critère inconnu : {identifiant}")
    return remplaces


def analyser_arguments() -> argparse.Namespace:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument(
        "--hors-ligne",
        action="store_true",
        default=os.environ.get("CONCORDE_HORS_LIGNE") == "1",
        help="n'interroge pas pip-audit et rend ce critère non évalué",
    )
    analyseur.add_argument(
        "--forcer-echec",
        metavar="IDENTIFIANT",
        help="force un critère en échec afin de vérifier le code de sortie de la porte",
    )
    return analyseur.parse_args()


def main() -> int:
    arguments = analyser_arguments()
    try:
        criteres = forcer_echec(mesurer_criteres(arguments.hors_ligne), arguments.forcer_echec)
    except ValueError as erreur:
        print(erreur, file=sys.stderr)
        return 2
    ecrire_rapports(criteres)
    sortie = code_retour(criteres)
    print(f"Porte de conformité : {'CONFORME' if sortie == 0 else 'NON CONFORME'} ({len(criteres)} critères)")
    return sortie


if __name__ == "__main__":
    raise SystemExit(main())
