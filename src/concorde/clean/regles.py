"""Moteur de regles de nettoyage : chaque regle se declare et se compte. (C3)

Le referentiel demande un tableau **avant / apres** et des regles ecrites. Plutot
que d'enchainer des appels pandas dont l'effet se perd, chaque regle est un objet
qui porte son identifiant, sa justification et sa fonction. Le moteur execute la
sequence et produit un rapport exploitable : lignes entrantes, lignes sortantes,
lignes supprimees, pourcentage, pour chaque regle.

Consequence pratique : le tableau du rapport est **genere**, jamais recopie a la
main. Il ne peut donc pas diverger du code.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass(frozen=True, slots=True)
class Regle:
    """Une regle de nettoyage nommee et justifiee."""

    identifiant: str
    libelle: str
    justification: str
    fonction: Callable[[pd.DataFrame], pd.DataFrame]
    #: `filtre` supprime des lignes ; `transformation` en modifie le contenu.
    nature: str = "filtre"


@dataclass(slots=True)
class TraceRegle:
    identifiant: str
    libelle: str
    nature: str
    lignes_avant: int
    lignes_apres: int
    justification: str

    @property
    def lignes_supprimees(self) -> int:
        return self.lignes_avant - self.lignes_apres

    @property
    def taux_suppression(self) -> float:
        return self.lignes_supprimees / self.lignes_avant if self.lignes_avant else 0.0


@dataclass(slots=True)
class RapportNettoyage:
    """Bilan complet d'un passage de nettoyage."""

    jeu: str
    lignes_initiales: int = 0
    lignes_finales: int = 0
    traces: list[TraceRegle] = field(default_factory=list)

    @property
    def lignes_supprimees(self) -> int:
        return self.lignes_initiales - self.lignes_finales

    def en_dict(self) -> dict[str, Any]:
        return {
            "jeu": self.jeu,
            "lignes_initiales": self.lignes_initiales,
            "lignes_finales": self.lignes_finales,
            "lignes_supprimees": self.lignes_supprimees,
            "taux_suppression_global": round(
                self.lignes_supprimees / self.lignes_initiales, 6
            ) if self.lignes_initiales else 0.0,
            "regles": [
                {
                    "identifiant": t.identifiant,
                    "libelle": t.libelle,
                    "nature": t.nature,
                    "lignes_avant": t.lignes_avant,
                    "lignes_apres": t.lignes_apres,
                    "lignes_supprimees": t.lignes_supprimees,
                    "taux_suppression": round(t.taux_suppression, 6),
                    "justification": t.justification,
                }
                for t in self.traces
            ],
        }

    def en_markdown(self) -> str:
        lignes = [
            f"### Jeu `{self.jeu}` — {self.lignes_initiales} lignes en entree, "
            f"{self.lignes_finales} en sortie "
            f"({self.lignes_supprimees} supprimees, "
            f"{self.lignes_supprimees / max(self.lignes_initiales, 1):.2%})",
            "",
            "| Regle | Nature | Avant | Apres | Supprimees | Justification |",
            "|---|---|---:|---:|---:|---|",
        ]
        for t in self.traces:
            lignes.append(
                f"| `{t.identifiant}` {t.libelle} | {t.nature} | {t.lignes_avant} | "
                f"{t.lignes_apres} | {t.lignes_supprimees} | {t.justification} |"
            )
        return "\n".join(lignes)


def appliquer(df: pd.DataFrame, regles: list[Regle], jeu: str) -> tuple[pd.DataFrame, RapportNettoyage]:
    """Applique les regles dans l'ordre et renvoie le resultat avec sa trace."""
    rapport = RapportNettoyage(jeu=jeu, lignes_initiales=len(df))
    courant = df
    for regle in regles:
        avant = len(courant)
        courant = regle.fonction(courant)
        rapport.traces.append(
            TraceRegle(
                identifiant=regle.identifiant,
                libelle=regle.libelle,
                nature=regle.nature,
                lignes_avant=avant,
                lignes_apres=len(courant),
                justification=regle.justification,
            )
        )
    rapport.lignes_finales = len(courant)
    return courant, rapport
