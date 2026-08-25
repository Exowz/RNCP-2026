"""Prevol reproductible de la demonstration locale."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections.abc import Callable, Iterable, Mapping
from pathlib import Path
from typing import Any

from concorde.service.lm_studio import ClientLMStudio, ServiceIADisponible

CHEMIN_LMS = str(Path("~/.lmstudio/bin/lms").expanduser())


class PrevolDemoErreur(RuntimeError):
    """Un prerequis de demonstration n'est pas pret."""


def _version_java(chemin: str) -> str:
    try:
        resultat = subprocess.run(  # noqa: S603 - chemin JDK local controle ci-dessous
            [f"{chemin}/bin/java", "-version"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ""
    correspondance = re.search(r'version "(\d+)', resultat.stdout + resultat.stderr)
    return correspondance.group(1) if correspondance else ""


def choisir_java_17(
    candidats: Iterable[str], version_java: Callable[[str], str] = _version_java
) -> str:
    """Retourne le premier JDK reellement en version majeure 17."""
    for candidat in candidats:
        if candidat and version_java(candidat).split(".", maxsplit=1)[0] == "17":
            return candidat
    raise PrevolDemoErreur(
        "Java 17 est introuvable. Installer un JDK 17 avant la demonstration Spark."
    )


def _resoudre_java_17_macos() -> str:
    candidats = [
        os.environ.get("JAVA_HOME", ""),
        "/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home",
        "/usr/local/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home",
    ]
    try:
        resultat = subprocess.run(  # noqa: S603 - outil macOS systeme, arguments fixes
            ["/usr/libexec/java_home", "-v", "17"],
            check=True,
            capture_output=True,
            text=True,
        )
        candidats.append(resultat.stdout.strip())
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    return choisir_java_17(candidats)


def environnement_java_17(
    resoudre_java: Callable[[], str] = _resoudre_java_17_macos,
    environnement_initial: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Retourne l'environnement dont Spark herite, avec Java 17 impose."""
    java_home = resoudre_java().strip()
    if not java_home:
        raise PrevolDemoErreur("Java 17 est introuvable."
        )
    environnement = dict(environnement_initial or os.environ)
    environnement["JAVA_HOME"] = java_home
    environnement["PATH"] = f"{java_home}/bin:{environnement.get('PATH', '')}"
    return environnement


def verifier_lm_studio(client: Any | None = None) -> None:
    """Verifie que la preuve locale C8 peut bien etre executee."""
    try:
        (client or ClientLMStudio()).verifier_service()
    except ServiceIADisponible as exc:
        raise PrevolDemoErreur(
            "LM Studio n'est pas pret. Demarrer le serveur local puis charger "
            "le modele google/gemma-4-e4b avant de relancer la commande."
        ) from exc


def modele_lm_studio_charge(etats: Iterable[Mapping[str, object]], modele: str) -> bool:
    """Verifie que `lms ps` contient le modele local dans un etat utilisable."""
    return any(
        etat.get("identifier") == modele and etat.get("status") in {"idle", "predicting"}
        for etat in etats
    )


def modele_lm_studio_a_charger(etats: Iterable[Mapping[str, object]], modele: str) -> bool:
    """Evite un second chargement du modele deja pret en memoire."""
    return not modele_lm_studio_charge(etats, modele)


def _lister_modeles_lm_studio(environnement: Mapping[str, str]) -> list[Mapping[str, object]]:
    try:
        resultat = subprocess.run(  # noqa: S603 - CLI LM Studio local, arguments internes fixes
            [CHEMIN_LMS, "ps", "--json"],
            check=True,
            capture_output=True,
            text=True,
            env=environnement,
        )
        etats = json.loads(resultat.stdout)
    except (FileNotFoundError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        raise PrevolDemoErreur("Le controle `lms ps` de LM Studio a echoue.") from exc
    if not isinstance(etats, list) or not all(isinstance(etat, dict) for etat in etats):
        raise PrevolDemoErreur("La sortie de `lms ps` est invalide.")
    return etats


def preparer_lm_studio(environnement: Mapping[str, str]) -> None:
    """Charge le modele pour la demo et controle l'etat expose par le CLI."""
    modele = ClientLMStudio().modele
    _executer([CHEMIN_LMS, "server", "start"], environnement)
    etats = _lister_modeles_lm_studio(environnement)
    if modele_lm_studio_a_charger(etats, modele):
        _executer([CHEMIN_LMS, "load", modele, "--ttl", "3600", "-y"], environnement)
        etats = _lister_modeles_lm_studio(environnement)
    if not modele_lm_studio_charge(etats, modele):
        raise PrevolDemoErreur(f"Le modele LM Studio attendu n'est pas charge : {modele}.")


def _executer(commande: list[str], environnement: Mapping[str, str]) -> None:
    try:
        subprocess.run(commande, check=True, env=environnement)  # noqa: S603 - liste interne fermee
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise PrevolDemoErreur(f"Commande de prevol en echec : {' '.join(commande)}") from exc


def lancer_prevol(ouvrir_lm_studio: bool = False, executer_tests: bool = True) -> None:
    """Prepare PostgreSQL, LM Studio et Spark, puis execute la suite de tests."""
    environnement = environnement_java_17()
    if ouvrir_lm_studio:
        _executer(["open", "-a", "LM Studio"], environnement)
    _executer(["docker", "compose", "up", "-d", "--wait", "postgres"], environnement)
    _executer([sys.executable, "scripts/import_postgres.py"], environnement)
    preparer_lm_studio(environnement)
    verifier_lm_studio()
    if executer_tests:
        _executer([sys.executable, "-m", "pytest", "-q"], environnement)
