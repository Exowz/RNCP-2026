"""Contrat du prevol local de soutenance."""

import pytest

from concorde.demo import (
    PrevolDemoErreur,
    choisir_java_17,
    environnement_java_17,
    verifier_lm_studio,
)
from concorde.service.lm_studio import ServiceIADisponible


def test_environnement_java_17_epingle_le_jdk_resolu() -> None:
    """Detecte un lanceur qui laisserait Spark demarrer avec le Java systeme."""
    environnement = environnement_java_17(
        resoudre_java=lambda: "/opt/jdks/openjdk-17/Contents/Home",
        environnement_initial={"PATH": "/usr/bin"},
    )

    assert environnement["JAVA_HOME"] == "/opt/jdks/openjdk-17/Contents/Home"
    assert environnement["PATH"].startswith("/opt/jdks/openjdk-17/Contents/Home/bin:")


def test_choisir_java_17_ignore_un_jdk_plus_recent() -> None:
    """Detecte le faux positif macOS qui retourne Java 26 pour une demande Java 17."""
    versions = {
        "/opt/jdks/openjdk-26": "26.0.2",
        "/opt/jdks/openjdk-17": "17.0.20",
    }

    java_home = choisir_java_17(
        ["/opt/jdks/openjdk-26", "/opt/jdks/openjdk-17"],
        version_java=lambda chemin: versions[chemin],
    )

    assert java_home == "/opt/jdks/openjdk-17"


def test_verifier_lm_studio_refuse_un_service_indisponible() -> None:
    """Detecte une suite lancee alors que la preuve C8 ne peut pas etre executee."""

    class ServiceAbsent:
        def verifier_service(self) -> dict[str, bool]:
            raise ServiceIADisponible("serveur absent")

    with pytest.raises(PrevolDemoErreur, match="LM Studio"):
        verifier_lm_studio(ServiceAbsent())
