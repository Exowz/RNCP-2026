"""Contrats d'entree et de sortie de l'API modele. (C9)

La validation est stricte et **refuse** plutot que de corriger. Un service qui
« repare » silencieusement une entree douteuse produit un resultat que personne
ne peut expliquer ensuite : c'est exactement le defaut que Concorde cherche a
rendre visible chez les autres.

Chaque champ porte sa contrainte, son exemple et sa description : la
documentation OpenAPI est donc generee a partir du contrat reellement applique,
et ne peut pas en diverger.
"""

from __future__ import annotations

from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

CodeCommune = Annotated[
    str,
    Field(
        pattern=r"^[0-9][0-9AB][0-9]{3}$",
        description="Code INSEE de la commune (5 caracteres, Corse incluse : 2A/2B).",
        examples=["33063"],
    ),
]


class RapprochementEntree(BaseModel):
    """Un rapprochement candidat soumis a evaluation.

    Le bloc DPE est optionnel : une mutation sans diagnostic rapproche est un cas
    metier normal, que le service traite en repondant `non_evaluable` plutot
    qu'en echouant.
    """

    model_config = ConfigDict(
        extra="forbid",  # un champ inconnu est une erreur, pas un silence
        json_schema_extra={
            "examples": [
                {
                    "id_mutation": "2023-100042",
                    "date_mutation": "2024-03-18",
                    "valeur_fonciere": 268000.0,
                    "surface_reelle_bati": 74.0,
                    "type_local": "Appartement",
                    "code_commune": "33063",
                    "id_parcelle": "33063000AB0412",
                    "numero_dpe": "2333E0000042",
                    "date_dpe": "2022-11-04",
                    "etiquette_dpe": "D",
                    "surface_habitable_dpe": 71.5,
                    "type_batiment_dpe": "appartement",
                    "annee_construction": 1975,
                    "score_ban": 0.95,
                    "conso_kwh_m2_an": 203.4,
                    "nb_dpe_candidats": 1,
                }
            ]
        },
    )

    # --- Mutation (DVF+) ---
    id_mutation: str = Field(min_length=1, max_length=64, description="Identifiant DVF+.")
    date_mutation: date = Field(description="Date de la mutation.")
    valeur_fonciere: float = Field(gt=0, le=1e9, description="Valeur fonciere en euros.")
    surface_reelle_bati: float = Field(
        gt=0, le=2000, description="Surface reelle batie en m2 (perimetre logement)."
    )
    type_local: Literal["Maison", "Appartement"] = Field(description="Type de local DVF+.")
    code_commune: CodeCommune
    id_parcelle: str = Field(min_length=1, max_length=32, description="Parcelle cadastrale.")

    # --- Diagnostic (ADEME), optionnel ---
    numero_dpe: str | None = Field(default=None, max_length=64, description="Numero ADEME.")
    date_dpe: date | None = Field(default=None, description="Date d'etablissement du DPE.")
    etiquette_dpe: Literal["A", "B", "C", "D", "E", "F", "G"] | None = Field(
        default=None, description="Etiquette energetique."
    )
    surface_habitable_dpe: float | None = Field(
        default=None, gt=0, le=2000, description="Surface habitable declaree au DPE (m2)."
    )
    type_batiment_dpe: Literal["maison", "appartement", "immeuble"] | None = Field(
        default=None, description="Type de batiment declare au DPE."
    )
    annee_construction: int | None = Field(
        default=None, ge=1000, le=2100, description="Annee de construction."
    )
    score_ban: float | None = Field(
        default=None, ge=0, le=1, description="Score de geocodage BAN du DPE."
    )
    conso_kwh_m2_an: float | None = Field(
        default=None, ge=0, le=2000, description="Consommation 5 usages (kWh/m2/an)."
    )
    nb_dpe_candidats: int = Field(
        default=1, ge=0, le=500,
        description="Nombre de DPE rattaches a la parcelle (mesure de l'ambiguite).",
    )

    @model_validator(mode="after")
    def _coherence_bloc_dpe(self) -> RapprochementEntree:
        """Le bloc DPE est tout ou rien sur ses champs indispensables."""
        if self.numero_dpe:
            manquants = [
                nom for nom, valeur in (("date_dpe", self.date_dpe),
                                        ("etiquette_dpe", self.etiquette_dpe))
                if valeur is None
            ]
            if manquants:
                raise ValueError(
                    f"Un numero de DPE est fourni : {manquants} doivent l'etre aussi. "
                    "Pour declarer une mutation sans diagnostic, omettre `numero_dpe`."
                )
        if self.date_dpe and self.date_dpe.year < 2000:
            raise ValueError("Date de DPE anterieure a 2000 : enregistrement non plausible.")
        return self


class LotEntree(BaseModel):
    """Lot de rapprochements. Borne volontairement pour limiter l'exposition
    a un deni de service par charge utile (OWASP A05)."""

    model_config = ConfigDict(extra="forbid")
    rapprochements: list[RapprochementEntree] = Field(min_length=1, max_length=200)


class MotifSortie(BaseModel):
    identifiant: str
    libelle: str
    gravite: Literal["majeur", "mineur"]
    message: str


class ReserveSortie(BaseModel):
    identifiant: str
    message: str
    penalite: float


class ConfianceSortie(BaseModel):
    score: float = Field(ge=0, le=1)
    niveau: Literal["eleve", "moyen", "faible", "insuffisant"]
    reserves: list[ReserveSortie]


class VariableAtypique(BaseModel):
    variable: str
    part_de_l_ecart: float
    valeur: float | None


class ExpositionAleas(BaseModel):
    niveau_max: int = Field(ge=0, le=4)
    nb_aleas_significatifs: int = Field(ge=0)


class ReferenceModele(BaseModel):
    version: str
    entraine_le: str


class VerdictSortie(BaseModel):
    """Reponse du service : trois axes distincts, jamais fusionnes en une note."""

    id_mutation: str
    numero_dpe: str | None = None
    statut: Literal["evalue", "non_evaluable"]
    score_anomalie: float | None = Field(
        default=None, description="Percentile d'atypicite dans [0,1] ; nul si non evaluable."
    )
    niveau_anomalie: Literal["normal", "a_verifier", "atypique", "non_evaluable"]
    score_coherence: float | None = Field(
        default=None, description="1 = aucune contradiction detectee."
    )
    motifs: list[MotifSortie] = Field(default_factory=list)
    confiance: ConfianceSortie
    exposition_aleas: ExpositionAleas
    variables_atypiques: list[VariableAtypique] = Field(default_factory=list)
    erreur_reconstruction: float | None = None
    explication: str
    modele: ReferenceModele


class ExplicationEntree(BaseModel):
    """Projection publique d'un verdict deja calcule, sans donnee source.

    Ce contrat borne explicitement ce qu'un service de reformulation local peut
    voir. Les identifiants de mutation, parcelle, adresse et variables brutes ne
    font pas partie de cette charge utile.
    """

    model_config = ConfigDict(extra="forbid")

    statut: Literal["evalue", "non_evaluable"]
    niveau_anomalie: Literal["normal", "a_verifier", "atypique", "non_evaluable"]
    score_coherence: float | None = Field(default=None, ge=0, le=1)
    motifs: list[MotifSortie] = Field(default_factory=list)
    confiance: ConfianceSortie
    explication: str = Field(min_length=1, max_length=1000)


class ExplicationSortie(BaseModel):
    """Texte de lecture optionnel, sans effet sur le verdict calcule."""

    texte: str = Field(min_length=1, max_length=1000)
    source: Literal["modele_local", "texte_assemble"]


class LotSortie(BaseModel):
    resultats: list[VerdictSortie]
    nb_evalues: int
    nb_non_evaluables: int


class Sante(BaseModel):
    statut: Literal["ok", "degrade"]
    service: str
    version_modele: str | None
    modele_charge: bool
    hors_ligne: bool
