"""Contrats de sortie de l'API de donnees Concorde. (C5)"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

from api.model.schemas import RapprochementEntree

NiveauConfiance = Literal["eleve", "moyen", "faible", "insuffisant"]


class PresentationRapprochement(BaseModel):
    """Libelles de restitution, separes de la charge utile du modele."""

    id_mutation: str
    id_rapprochement: str
    nom_commune: str
    code_commune: str
    code_departement: str
    etiquette_dpe: str | None = None
    type_local: str
    date_mutation: date
    surface_reelle_bati: float
    valeur_fonciere: float
    a_dpe: bool
    niveau_confiance: NiveauConfiance


class RapprochementListe(BaseModel):
    """Resume d'un rapprochement dans la liste paginee."""

    id_mutation: str
    id_rapprochement: str
    nom_commune: str
    code_commune: str
    code_departement: str
    etiquette_dpe: str | None = None
    type_local: str
    date_mutation: date
    surface_reelle_bati: float
    valeur_fonciere: float
    a_dpe: bool
    niveau_confiance: NiveauConfiance


class PageRapprochements(BaseModel):
    """Page bornee pour afficher la liste sans exposer la table complete."""

    page: int = Field(ge=1)
    taille: int = Field(ge=1)
    total: int = Field(ge=0)
    resultats: list[RapprochementListe]


class DetailRapprochement(BaseModel):
    """Presentation humaine et charge utile strictement acceptee par ``/predict``."""

    presentation: PresentationRapprochement
    donnees: RapprochementEntree


class CasDemonstration(BaseModel):
    """Un cas pedagogique reel, selectionne par ``app.exemples``."""

    identifiant: str
    intitule: str
    presentation: PresentationRapprochement
    donnees: RapprochementEntree


class DemonstrationRapprochements(BaseModel):
    cas: list[CasDemonstration] = Field(min_length=5, max_length=5)
