"""Couche de cohérence explicite : des règles metier, pas un modèle. (C9)

Un detecteur d'anomalie statistique dit « cette ligne est atypique ». Il ne dit
jamais **pourquoi**. Pour un produit dont la these est « je rends visibles les
hypotheses et les inconnues », c'est insuffisant : l'utilisateur a besoin du
motif, pas du score.

D'ou cette couche, volontairement anterieure au modèle appris : des règles
nommees, seuillees, justifiees, qui produisent des motifs lisibles. Le detecteur
statistique vient ensuite, pour attraper ce que les règles ne prevoient pas.

Chaque seuil est defendable a l'oral. Il est ecrit ici, une seule fois.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal

Gravite = Literal["majeur", "mineur"]

#: Poids d'un motif dans la degradation du score de coherence.
POIDS_GRAVITE: dict[Gravite, float] = {"majeur": 0.40, "mineur": 0.15}


@dataclass(frozen=True, slots=True)
class RegleCoherence:
    """Une contradiction possible entre les deux enregistrements rapproches."""

    identifiant: str
    libelle: str
    gravite: Gravite
    seuil: str
    justification: str
    predicat: Callable[[dict[str, Any]], bool]
    message: Callable[[dict[str, Any]], str]


#: Ecart de surface tolere entre la surface reelle batie (DVF) et la surface
#: habitable (DPE). Les deux notions different par construction : combles,
#: sous-sols et annexes comptent dans l'une et pas dans l'autre. Un ecart
#: modere est donc normal ; au-dela, c'est le rapprochement qui est douteux.
SEUIL_ECART_SURFACE = 0.20

#: Duree de validite reglementaire d'un DPE. Au-dela, le diagnostic peut ne
#: plus decrire l'etat du bien (travaux, changement de systeme de chauffage).
SEUIL_ANCIENNETE_DPE_ANNEES = 10.0

#: Bornes de l'ecart au prix median communal au-dela desquelles la mutation
#: n'est probablement pas une vente ordinaire de gre a gre (viager, demembrement,
#: vente entre proches, lot mal decoupe).
SEUIL_PRIX_HAUT = 2.0
SEUIL_PRIX_BAS = -0.70


REGLES: tuple[RegleCoherence, ...] = (
    RegleCoherence(
        identifiant="COH-01",
        libelle="écart de surface entre DVF et DPE",
        gravite="majeur",
        seuil=f"|écart| / max(surfaces) > {SEUIL_ECART_SURFACE:.0%}",
        justification=(
            "La surface réelle bâtie (DVF+) et la surface habitable (DPE) ne mesurent pas "
            "la même chose : un écart modéré est attendu. Un écart supérieur au seuil "
            "signale plus probablement deux logements différents qu'une différence de "
            "convention de mesure."
        ),
        predicat=lambda v: _fini(v.get("ecart_surface_rel")) > SEUIL_ECART_SURFACE,
        message=lambda v: (
            f"La surface DVF et la surface habitable du DPE different de "
            f"{v['ecart_surface_rel']:.0%} : le rapprochement peut porter sur deux logements "
            f"distincts de la même parcelle."
        ),
    ),
    RegleCoherence(
        identifiant="COH-02",
        libelle="désaccord sur le type de logement",
        gravite="majeur",
        seuil="type_local (DVF) != type_batiment (DPE)",
        justification=(
            "DVF+ et l'ADEME qualifient tous deux le bien en maison ou appartement. "
            "Un désaccord sur cette qualification n'est pas une nuance de vocabulaire : "
            "l'un des deux enregistrements ne décrit pas le bien attendu."
        ),
        predicat=lambda v: _fini(v.get("desaccord_type_local")) >= 1.0,
        message=lambda v: (
            "Le type de logement déclaré dans DVF+ ne correspond pas à celui du DPE."
        ),
    ),
    RegleCoherence(
        identifiant="COH-03",
        libelle="DPE établi après la mutation",
        gravite="mineur",
        seuil="date_DPE > date_mutation",
        justification=(
            "Un DPE postérieur à la vente ne décrit pas le bien tel qu'il a été vendu. "
            "Ce n'est pas une erreur (le nouveau propriétaire peut faire refaire le "
            "diagnostic) mais toute lecture énergétique de la transaction devient "
            "anachronique."
        ),
        predicat=lambda v: _fini(v.get("dpe_posterieur_mutation")) >= 1.0,
        message=lambda v: (
            f"Le DPE a été établi après la mutation ({v.get('ecart_temporel_annees', 0):.1f} an(s) "
            "plus tard) : il ne décrit pas l'etat du bien au moment de la vente."
        ),
    ),
    RegleCoherence(
        identifiant="COH-04",
        libelle="DPE antérieur de plus de 10 ans",
        gravite="mineur",
        seuil=f"écart temporel > {SEUIL_ANCIENNETE_DPE_ANNEES:.0f} ans",
        justification=(
            "Duree de validité réglementaire d'un DPE. Au-delà, des travaux ont pu "
            "modifier la performance du logement sans que le diagnostic le reflète."
        ),
        predicat=lambda v: (
            _fini(v.get("dpe_posterieur_mutation")) < 1.0
            and _fini(v.get("ecart_temporel_annees")) > SEUIL_ANCIENNETE_DPE_ANNEES
        ),
        message=lambda v: (
            f"Le DPE date de {v.get('ecart_temporel_annees', 0):.1f} ans avant la mutation, "
            "au-dela de sa durée de validité réglementaire."
        ),
    ),
    RegleCoherence(
        identifiant="COH-05",
        libelle="prix au m2 tres eloigne de la médiane communale",
        gravite="mineur",
        seuil=f"écart relatif > +{SEUIL_PRIX_HAUT:.0%} ou < {SEUIL_PRIX_BAS:.0%}",
        justification=(
            "Le prix n'est pas prédit : il sert uniquement de signal de cohérence. "
            "Un écart extrême à la médiane communale signale généralement une mutation "
            "qui n'est pas une vente ordinaire (viager, démembrement, vente entre "
            "proches, lot mal découpé) plutôt qu'un bien exceptionnel."
        ),
        predicat=lambda v: (
            _fini(v.get("ecart_prix_m2_commune")) > SEUIL_PRIX_HAUT
            or _fini(v.get("ecart_prix_m2_commune")) < SEUIL_PRIX_BAS
        ),
        message=lambda v: (
            f"Le prix au m² s'écarte de {v['ecart_prix_m2_commune']:+.0%} de la médiane "
            "communale : la mutation n'est probablement pas une vente ordinaire."
        ),
    ),
)


def _fini(valeur: Any) -> float:
    """Convertit en flottant en traitant NaN et None comme 0 (règle non declenchee)."""
    try:
        f = float(valeur)
    except (TypeError, ValueError):
        return 0.0
    return f if f == f else 0.0  # NaN != NaN


@dataclass(frozen=True, slots=True)
class Motif:
    """Un motif de non-cohérence, destiné à l'utilisateur final."""

    identifiant: str
    libelle: str
    gravite: Gravite
    message: str

    def en_dict(self) -> dict[str, str]:
        return {
            "identifiant": self.identifiant,
            "libelle": self.libelle,
            "gravite": self.gravite,
            "message": self.message,
        }


def evaluer(variables: dict[str, Any]) -> tuple[float, list[Motif]]:
    """Applique les règles de cohérence à un rapprochement.

    Returns:
        Le score de cohérence dans [0, 1] (1 = aucune contradiction détectée)
        et la liste des motifs declenches.
    """
    motifs: list[Motif] = []
    penalite = 0.0
    for regle in REGLES:
        if regle.predicat(variables):
            motifs.append(
                Motif(
                    identifiant=regle.identifiant,
                    libelle=regle.libelle,
                    gravite=regle.gravite,
                    message=regle.message(variables),
                )
            )
            penalite += POIDS_GRAVITE[regle.gravite]
    return max(0.0, 1.0 - min(1.0, penalite)), motifs


def catalogue() -> list[dict[str, str]]:
    """Renvoie le catalogue documente des règles, expose par l'API et l'application."""
    return [
        {
            "identifiant": r.identifiant,
            "libelle": r.libelle,
            "gravite": r.gravite,
            "seuil": r.seuil,
            "justification": r.justification,
        }
        for r in REGLES
    ]
