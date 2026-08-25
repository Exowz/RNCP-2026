"""API REST des donnees preparees pour Concorde. (C5)"""

from __future__ import annotations

from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Annotated

import pandas as pd
from app.exemples import _vers_entree
from app.exemples import charger as charger_exemples
from fastapi import Depends, FastAPI, HTTPException, Query, status

from api.data.schemas import (
    CasDemonstration,
    DemonstrationRapprochements,
    DetailRapprochement,
    PageRapprochements,
    PresentationRapprochement,
    RapprochementListe,
)
from concorde.clean.rapprochement import SORTIE as TABLE_RAPPROCHEMENTS
from concorde.common.offline import enable_offline_guard
from concorde.features.construction import calculer_references, construire_variables
from concorde.model.confiance import evaluer as evaluer_confiance
from concorde.queries import executer_requete_postgres
from concorde.service.observabilite import Metriques, ObservabiliteMiddleware
from concorde.service.securite import EntetesSecuriteMiddleware, Identite, exige_role

SERVICE = "api-data"
metriques = Metriques(SERVICE)


@asynccontextmanager
async def cycle_de_vie(app: FastAPI):
    enable_offline_guard()
    yield


app = FastAPI(
    title="Concorde — API data",
    version="0.1.0",
    description=(
        "Expose les references communales et l'exposition aux aleas preparees dans PostgreSQL. "
        "Les routes metier exigent une cle API `X-API-Key`."
    ),
    lifespan=cycle_de_vie,
)
app.add_middleware(EntetesSecuriteMiddleware)
app.add_middleware(ObservabiliteMiddleware, service=SERVICE, metriques=metriques)


@app.get("/sante", tags=["exploitation"])
def sante() -> dict[str, str]:
    """Sonde sans secret, utilisable par Docker et la CI."""
    return {"statut": "ok", "service": SERVICE}


@app.get("/communes", tags=["donnees"])
def communes(
    departement: Annotated[str, Query(pattern=r"^[0-9]{2}$", examples=["33"])],
    identite: Annotated[Identite, Depends(exige_role("reader"))],
) -> list[dict]:
    """Liste les communes d'un departement et leur synthese d'aleas."""
    resultat = executer_requete_postgres(departement)
    metriques.incrementer("lectures_communes")
    return resultat.to_dict(orient="records")


@lru_cache(maxsize=1)
def _lire_rapprochements() -> pd.DataFrame:
    """Charge une seule fois la table figee et derive son niveau de confiance.

    Le calcul reutilise les variables et la regle de confiance effectivement
    executees par l'API modele. Ainsi un filtre de liste ne promet pas un niveau
    different de celui affiche apres ``POST /predict``.
    """
    if not TABLE_RAPPROCHEMENTS.exists():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Table de rapprochements indisponible. Executer le nettoyage avant l'API.",
        )

    table = pd.read_parquet(TABLE_RAPPROCHEMENTS)
    variables = construire_variables(table, calculer_references(table))
    table = table.copy()
    table["niveau_confiance"] = [
        evaluer_confiance(ligne.to_dict(), a_dpe=bool(ligne["a_dpe"])).niveau
        for _, ligne in variables.iterrows()
    ]
    return table


def _presentation(ligne: pd.Series) -> PresentationRapprochement:
    """Transforme une ligne Pandas en objet stable pour une interface humaine."""
    return PresentationRapprochement(
        id_mutation=str(ligne["id_mutation"]),
        id_rapprochement=str(ligne["id_rapprochement"]),
        nom_commune=str(ligne["nom_commune"]),
        code_commune=str(ligne["code_commune"]).zfill(5),
        code_departement=str(ligne["code_departement"]).zfill(2),
        etiquette_dpe=_texte_ou_rien(ligne.get("etiquette_dpe")),
        type_local=str(ligne["type_local"]),
        date_mutation=pd.Timestamp(ligne["date_mutation"]).date(),
        surface_reelle_bati=float(ligne["surface_reelle_bati"]),
        valeur_fonciere=float(ligne["valeur_fonciere"]),
        a_dpe=bool(ligne["a_dpe"]),
        niveau_confiance=str(ligne["niveau_confiance"]),
    )


def _texte_ou_rien(valeur: object) -> str | None:
    """Remplace les NaN Pandas par ``null`` avant la serialisation JSON."""
    return None if pd.isna(valeur) else str(valeur)


def _detail(ligne: pd.Series) -> DetailRapprochement:
    """Associe la restitution lisible et le payload exact de l'API modele."""
    return DetailRapprochement(
        presentation=_presentation(ligne),
        donnees=_vers_entree(ligne),
    )


@app.get(
    "/rapprochements/demonstration",
    response_model=DemonstrationRapprochements,
    tags=["donnees"],
    summary="Les cinq cas reels de demonstration",
)
def demonstration_rapprochements(
    identite: Annotated[Identite, Depends(exige_role("reader"))],
) -> DemonstrationRapprochements:
    """Expose la selection deterministe de ``app.exemples`` sans la dupliquer."""
    table = _lire_rapprochements()
    par_mutation = table.set_index("id_mutation", drop=False)
    cas: list[CasDemonstration] = []
    for identifiant, exemple in charger_exemples().items():
        identifiant_mutation = exemple["donnees"]["id_mutation"]
        ligne = par_mutation.loc[identifiant_mutation]
        if isinstance(ligne, pd.DataFrame):
            ligne = ligne.sort_values("id_rapprochement").iloc[0]
        cas.append(
            CasDemonstration(
                identifiant=identifiant,
                intitule=exemple["intitule"],
                presentation=_presentation(ligne),
                donnees=exemple["donnees"],
            )
        )
    if len(cas) != 5:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Les cinq cas de demonstration ne sont pas disponibles dans la table.",
        )
    metriques.incrementer("lectures_demonstration")
    return DemonstrationRapprochements(cas=cas)


@app.get(
    "/rapprochements/{id_mutation}",
    response_model=DetailRapprochement,
    tags=["donnees"],
    summary="Detail d'un rapprochement pour l'evaluation",
    responses={404: {"description": "Mutation absente de la table preparee."}},
)
def detail_rapprochement(
    id_mutation: str,
    identite: Annotated[Identite, Depends(exige_role("reader"))],
) -> DetailRapprochement:
    """Retourne ``donnees``, directement validables par ``POST /predict``."""
    candidats = _lire_rapprochements().query("id_mutation == @id_mutation")
    if candidats.empty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mutation introuvable.")
    ligne = candidats.sort_values("id_rapprochement").iloc[0]
    metriques.incrementer("lectures_rapprochement")
    return _detail(ligne)


@app.get(
    "/rapprochements",
    response_model=PageRapprochements,
    tags=["donnees"],
    summary="Liste paginee des rapprochements prepares",
)
def liste_rapprochements(
    identite: Annotated[Identite, Depends(exige_role("reader"))],
    code_commune: Annotated[str | None, Query(pattern=r"^[0-9][0-9AB][0-9]{3}$")] = None,
    niveau_confiance: Annotated[
        str | None, Query(pattern=r"^(eleve|moyen|faible|insuffisant)$")
    ] = None,
    avec_dpe: bool | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    taille: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PageRapprochements:
    """Filtre la table sans exposer ses identifiants seuls a l'interface."""
    resultat = _lire_rapprochements()
    if code_commune is not None:
        resultat = resultat[resultat["code_commune"] == code_commune]
    if niveau_confiance is not None:
        resultat = resultat[resultat["niveau_confiance"] == niveau_confiance]
    if avec_dpe is not None:
        resultat = resultat[resultat["a_dpe"] == avec_dpe]
    resultat = resultat.sort_values("id_rapprochement")
    total = len(resultat)
    debut = (page - 1) * taille
    elements = [
        RapprochementListe(**_presentation(ligne).model_dump())
        for _, ligne in resultat.iloc[debut : debut + taille].iterrows()
    ]
    metriques.incrementer("lectures_rapprochements")
    return PageRapprochements(page=page, taille=taille, total=total, resultats=elements)
