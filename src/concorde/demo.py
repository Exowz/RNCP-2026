"""Prevol reproductible de la demonstration locale."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from collections.abc import Callable, Iterable, Mapping
from typing import Any

from concorde.service.lm_studio import ClientLMStudio, ServiceIADisponible


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
    verifier_lm_studio()
    if executer_tests:
        _executer([sys.executable, "-m", "pytest", "-q"], environnement)
