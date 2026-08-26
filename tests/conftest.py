"""Configuration partagee par toute la suite de tests.

Spark 3.5 refuse le JDK 26 du poste (Hadoop appelle encore
``Subject.getSubject``, retire depuis Java 24). ``scripts/spark-env.sh`` fixe
``JAVA_HOME`` sur le JDK 17, mais rien ne garantit qu'il ait ete source avant
``pytest`` : deux tests du bloc 1 echouaient alors pour une raison
d'environnement, pas de code. On refait donc ici la meme selection, afin que la
suite soit verte depuis un shell neuf.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

#: Emplacements ou un JDK 17 peut se trouver sur un poste macOS.
CANDIDATS_JDK_17 = (
    "/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home",
    "/usr/local/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home",
)


def _est_un_jdk_17(racine: str) -> bool:
    """Interroge le binaire plutot que de se fier au chemin."""
    binaire = Path(racine) / "bin" / "java"
    if not binaire.is_file() or not os.access(binaire, os.X_OK):
        return False
    try:
        sortie = subprocess.run(
            [str(binaire), "-version"], capture_output=True, text=True, timeout=15
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return 'version "17.' in (sortie.stderr + sortie.stdout)


def _java_home_pour_spark() -> str | None:
    candidats = [os.environ.get("JAVA_HOME", "")]
    candidats.extend(CANDIDATS_JDK_17)
    if shutil.which("/usr/libexec/java_home"):
        try:
            trouve = subprocess.run(
                ["/usr/libexec/java_home", "-v", "17"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            candidats.append(trouve.stdout.strip())
        except (OSError, subprocess.SubprocessError):
            pass
    return next((c for c in candidats if c and _est_un_jdk_17(c)), None)


def pytest_configure(config) -> None:  # noqa: ARG001 - signature imposee par pytest
    """Aligne l'environnement Java avant la collecte des tests Spark."""
    if not _est_un_jdk_17(os.environ.get("JAVA_HOME", "")):
        racine = _java_home_pour_spark()
        if racine is not None:
            os.environ["JAVA_HOME"] = racine
            os.environ["PATH"] = f"{racine}/bin:{os.environ.get('PATH', '')}"
    # Hors ligne, Spark ne doit pas tenter de publier l'adresse mDNS du poste.
    os.environ.setdefault("SPARK_LOCAL_IP", "127.0.0.1")
