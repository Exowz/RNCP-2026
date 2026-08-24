"""Niveau de confiance : ce que l'on ne sait pas, rendu explicite. (C9)

La confiance n'est pas la probabilite que le bien soit anormal. C'est le credit
que l'on peut accorder au resultat lui-meme, compte tenu de ce qui manque.

Un rapprochement peut etre parfaitement coherent et neanmoins peu fiable : deux
DPE sur la meme parcelle, un geocodage grossier, une annee de construction
absente. Confondre les deux notions produirait exactement le defaut que le projet
denonce : une reponse trop assuree sur une donnee trop pauvre.

Les penalites sont additives, plafonnees, et chacune est restituee a
l'utilisateur avec sa raison.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

Niveau = Literal["eleve", "moyen", "faible", "insuffisant"]

#: Seuils de passage entre niveaux de confiance.
SEUILS: tuple[tuple[float, Niveau], ...] = (
    (0.75, "eleve"),
    (0.50, "moyen"),
    (0.25, "faible"),
)

#: En dessous de ce score BAN, le geocodage de l'adresse du DPE est juge
#: approximatif par l'ADEME elle-meme : le rattachement a la parcelle devient
#: incertain.
SEUIL_SCORE_BAN = 0.80

#: Ecart temporel au-dela duquel le DPE decrit un etat du bien trop eloigne
#: de la mutation pour etre lu sans reserve.
SEUIL_ECART_TEMPOREL_ANNEES = 8.0


@dataclass(frozen=True, slots=True)
class Reserve:
    """Une raison, lisible, de ne pas accorder un credit total au resultat."""

    identifiant: str
    message: str
    penalite: float

    def en_dict(self) -> dict[str, Any]:
        return {
            "identifiant": self.identifiant,
            "message": self.message,
            "penalite": round(self.penalite, 3),
        }


@dataclass(frozen=True, slots=True)
class Confiance:
    score: float
    niveau: Niveau
    reserves: list[Reserve]

    def en_dict(self) -> dict[str, Any]:
        return {
            "score": round(self.score, 3),
            "niveau": self.niveau,
            "reserves": [r.en_dict() for r in self.reserves],
        }


def _fini(valeur: Any, defaut: float = float("nan")) -> float:
    try:
        f = float(valeur)
    except (TypeError, ValueError):
        return defaut
    return f if f == f else defaut


def niveau_depuis_score(score: float) -> Niveau:
    for seuil, niveau in SEUILS:
        if score >= seuil:
            return niveau
    return "insuffisant"


def evaluer(variables: dict[str, Any], a_dpe: bool) -> Confiance:
    """Calcule le niveau de confiance d'un rapprochement.

    Args:
        variables: variables calculees pour ce rapprochement.
        a_dpe: vrai si un DPE a effectivement ete apparie.
    """
    if not a_dpe:
        return Confiance(
            score=0.0,
            niveau="insuffisant",
            reserves=[
                Reserve(
                    "CONF-00",
                    "Aucun DPE n'a pu etre rapproche de cette mutation. Aucune verification "
                    "de coherence n'est possible : le systeme ne conclut pas.",
                    1.0,
                )
            ],
        )

    reserves: list[Reserve] = []
    penalite = 0.0

    score_ban = _fini(variables.get("score_ban"))
    if score_ban != score_ban:  # NaN : score absent
        reserves.append(Reserve("CONF-01", "Le score de geocodage BAN du DPE est absent.", 0.15))
        penalite += 0.15
    elif score_ban < SEUIL_SCORE_BAN:
        reserves.append(
            Reserve(
                "CONF-02",
                f"Le geocodage de l'adresse du DPE est approximatif (score BAN {score_ban:.2f} "
                f"< {SEUIL_SCORE_BAN:.2f}) : le rattachement a la parcelle est incertain.",
                0.25,
            )
        )
        penalite += 0.25

    nb_candidats = _fini(variables.get("nb_dpe_candidats"), 0.0)
    if nb_candidats > 1:
        reserves.append(
            Reserve(
                "CONF-03",
                f"La parcelle porte {int(nb_candidats)} DPE : le rapprochement retenu est un "
                "choix parmi plusieurs, pas une certitude.",
                0.20,
            )
        )
        penalite += 0.20

    manquants = _fini(variables.get("nb_champs_manquants"), 0.0)
    if manquants > 0:
        p = min(0.30, 0.10 * manquants)
        reserves.append(
            Reserve(
                "CONF-04",
                f"Des champs necessaires a la comparaison sont absents du DPE "
                f"(poids cumule {manquants:.1f}).",
                p,
            )
        )
        penalite += p

    ecart = _fini(variables.get("ecart_temporel_annees"), 0.0)
    if ecart > SEUIL_ECART_TEMPOREL_ANNEES:
        reserves.append(
            Reserve(
                "CONF-05",
                f"Le DPE et la mutation sont separes de {ecart:.1f} ans : l'etat decrit peut "
                "avoir change.",
                0.10,
            )
        )
        penalite += 0.10

    score = max(0.0, 1.0 - min(1.0, penalite))
    return Confiance(score=score, niveau=niveau_depuis_score(score), reserves=reserves)
