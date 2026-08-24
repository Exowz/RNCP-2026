"""Chemins canoniques du projet.

Un seul endroit definit ou vivent les donnees, les modeles et les logs.
Tout le reste du code importe d'ici : aucun chemin en dur ailleurs.
"""

from __future__ import annotations

from pathlib import Path

# src/concorde/common/paths.py -> remonter 4 niveaux
PROJECT_ROOT: Path = Path(__file__).resolve().parents[3]

DATA_DIR: Path = PROJECT_ROOT / "data"
DATA_RAW: Path = DATA_DIR / "raw"
DATA_PROCESSED: Path = DATA_DIR / "processed"
DATA_SAMPLES: Path = DATA_DIR / "samples"
DATA_EXTERNAL: Path = DATA_DIR / "external"

MODELS_DIR: Path = PROJECT_ROOT / "models"
DOCS_DIR: Path = PROJECT_ROOT / "docs"
REPORTS_DIR: Path = PROJECT_ROOT / "reports"

MONITORING_DIR: Path = PROJECT_ROOT / "monitoring"
LOGS_DIR: Path = MONITORING_DIR / "logs"
MONITORING_APP: Path = MONITORING_DIR / "app"
MONITORING_MODEL: Path = MONITORING_DIR / "model"


def ensure_dirs() -> None:
    """Cree les repertoires de travail s'ils n'existent pas (idempotent)."""
    for path in (
        DATA_RAW,
        DATA_PROCESSED,
        DATA_SAMPLES,
        DATA_EXTERNAL,
        MODELS_DIR,
        LOGS_DIR,
        MONITORING_APP,
        MONITORING_MODEL,
    ):
        path.mkdir(parents=True, exist_ok=True)
