"""Genere le rapport Evidently local."""

from concorde.common.paths import MONITORING_MODEL
from concorde.monitoring_modele import generer_rapport_derives

if __name__ == "__main__":
    print(generer_rapport_derives(MONITORING_MODEL))
