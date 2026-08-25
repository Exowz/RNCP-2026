"""API modele : expose le moteur de confiance en HTTP. (C9)

    uvicorn api.model.main:app --host 127.0.0.1 --port 8002

Le modele est charge **une fois** au demarrage, depuis l'artefact gele
`models/concorde_moteur.pt`. Aucun chargement distant, aucun telechargement de
poids : le service demarre et repond sans acces reseau.

Si l'artefact est absent, le service demarre quand meme mais se declare
`degrade` sur `/sante` et refuse les predictions avec un 503 explicite. Un
service qui refuse de demarrer ne dit pas ce qui lui manque ; celui-ci le dit.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Annotated, Any

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from api.model.schemas import (
    ExplicationEntree,
    ExplicationSortie,
    LotEntree,
    LotSortie,
    RapprochementEntree,
    Sante,
    VerdictSortie,
)
from concorde.common.config import get_settings
from concorde.common.logging_setup import setup_logging
from concorde.common.offline import enable_offline_guard
from concorde.common.paths import MONITORING_MODEL
from concorde.model import regles_coherence
from concorde.model.moteur import Moteur
from concorde.service.lm_studio import ClientLMStudio, ServiceIADisponible
from concorde.service.observabilite import Metriques, ObservabiliteMiddleware
from concorde.service.securite import (
    NOM_ENTETE,
    EntetesSecuriteMiddleware,
    Identite,
    exige_role,
)

SERVICE = "api-model"
log = setup_logging(SERVICE)
metriques = Metriques(SERVICE)

#: Etat du service, rempli au demarrage.
etat: dict[str, Any] = {"moteur": None, "erreur_chargement": None}


@asynccontextmanager
async def cycle_de_vie(app: FastAPI):
    # La contrainte hors ligne est imposee avant tout chargement : une future
    # dependance qui tenterait de joindre Internet echoue donc au demarrage,
    # tandis que les appels app -> API sur 127.0.0.1 restent autorises.
    enable_offline_guard()
    try:
        etat["moteur"] = Moteur.charger()
        log.info(
            f"Modele charge : version {etat['moteur'].fiche.version}",
            extra={"event": "modele_charge", "version": etat["moteur"].fiche.version,
                   "commit": etat["moteur"].fiche.commit_git},
        )
    except Exception as exc:  # noqa: BLE001 - le service doit pouvoir dire ce qui lui manque
        etat["erreur_chargement"] = str(exc)
        log.error(f"Modele non charge : {exc}",
                  extra={"event": "modele_absent", "erreur": str(exc)})
    yield
    metriques.deverser(MONITORING_MODEL / "metriques_api_model.json")
    log.info("Arret du service", extra={"event": "arret"})


DESCRIPTION = f"""
Service d'evaluation de la fiabilite d'un rapprochement entre une **mutation
immobiliere DVF+** et un **diagnostic de performance energetique ADEME**.

Le service **ne predit ni prix ni valeur**. Il repond a trois questions
distinctes, volontairement jamais fusionnees en une note unique :

| Axe | Question | Sortie |
|---|---|---|
| Coherence | Les deux enregistrements se contredisent-ils ? | `score_coherence`, `motifs` |
| Anomalie | Ce rapprochement ressemble-t-il aux autres ? | `score_anomalie`, `variables_atypiques` |
| Confiance | Peut-on se fier a cette reponse ? | `confiance.niveau`, `confiance.reserves` |

## Authentification

Toutes les routes metier exigent l'en-tete `{NOM_ENTETE}`.
Roles : `reader` (prediction et explication), `analyst` (metriques et lots), `admin`.

## Fonctionnement hors ligne

Le modele est charge depuis un artefact local gele. Le service n'emet aucune
requete sortante.
"""

app = FastAPI(
    title="Concorde — API modele de confiance",
    version="0.1.0",
    description=DESCRIPTION,
    lifespan=cycle_de_vie,
    openapi_tags=[
        {"name": "prediction", "description": "Evaluation d'un ou plusieurs rapprochements."},
        {"name": "explication", "description": "Reformulation locale optionnelle d'un verdict deja calcule."},
        {"name": "transparence", "description": "Fiche du modele et catalogue des regles."},
        {"name": "exploitation", "description": "Sante et metriques du service."},
    ],
)
app.add_middleware(EntetesSecuriteMiddleware)
app.add_middleware(ObservabiliteMiddleware, service=SERVICE, metriques=metriques)


def moteur_requis() -> Moteur:
    """Dependance : refuse proprement si l'artefact n'a pas pu etre charge."""
    if etat["moteur"] is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Modele indisponible : "
                f"{etat['erreur_chargement']}. Executer "
                "`python -m concorde.model.entrainement` puis redemarrer le service."
            ),
        )
    return etat["moteur"]


# --------------------------------------------------------------- exploitation


@app.get("/sante", response_model=Sante, tags=["exploitation"], summary="Etat du service")
def sante() -> Sante:
    """Sonde de sante, sans authentification : elle sert au demarrage et a la CI."""
    moteur = etat["moteur"]
    return Sante(
        statut="ok" if moteur else "degrade",
        service=SERVICE,
        version_modele=moteur.fiche.version if moteur else None,
        modele_charge=moteur is not None,
        hors_ligne=get_settings().offline,
    )


@app.get("/metriques", tags=["exploitation"], summary="Metriques et alertes du service")
def lire_metriques(
    identite: Annotated[Identite, Depends(exige_role("analyst"))],
) -> dict[str, Any]:
    """Instantane des compteurs, latences et alertes actives. (C11, C20)"""
    instantane = metriques.instantane()
    metriques.deverser(MONITORING_MODEL / "metriques_api_model.json")
    return instantane


# --------------------------------------------------------------- transparence


@app.get("/modele/fiche", tags=["transparence"], summary="Fiche du modele servi")
def fiche_modele(
    identite: Annotated[Identite, Depends(exige_role("reader"))],
    moteur: Annotated[Moteur, Depends(moteur_requis)],
) -> dict[str, Any]:
    """Version, date d'entrainement, variables, metriques et **limites assumees**."""
    return moteur.fiche.en_dict()


@app.get("/regles", tags=["transparence"], summary="Catalogue des regles de coherence")
def catalogue_regles(
    identite: Annotated[Identite, Depends(exige_role("reader"))],
) -> list[dict[str, str]]:
    """Chaque regle avec son seuil et sa justification metier."""
    return regles_coherence.catalogue()


# ----------------------------------------------------------------- prediction


@app.post(
    "/expliquer",
    response_model=ExplicationSortie,
    tags=["explication"],
    summary="Reformuler un verdict deja calcule",
    responses={
        401: {"description": f"En-tete {NOM_ENTETE} absent ou cle invalide."},
        422: {"description": "Projection de verdict invalide."},
    },
)
def expliquer(
    verdict: ExplicationEntree,
    identite: Annotated[Identite, Depends(exige_role("reader"))],
) -> ExplicationSortie:
    """Ameliore la lisibilite sans recalculer ni modifier le verdict recu."""
    try:
        texte = ClientLMStudio().reformuler_verdict(verdict.model_dump())
    except ServiceIADisponible:
        return ExplicationSortie(texte=verdict.explication, source="texte_assemble")
    return ExplicationSortie(texte=texte, source="modele_local")


@app.post(
    "/predict",
    response_model=VerdictSortie,
    tags=["prediction"],
    summary="Evaluer un rapprochement",
    responses={
        401: {"description": f"En-tete {NOM_ENTETE} absent ou cle invalide."},
        422: {"description": "Entree invalide : le detail indique le champ fautif."},
        503: {"description": "Artefact de modele indisponible."},
    },
)
def predict(
    entree: RapprochementEntree,
    identite: Annotated[Identite, Depends(exige_role("reader"))],
    moteur: Annotated[Moteur, Depends(moteur_requis)],
) -> VerdictSortie:
    """Evalue la coherence, l'atypicite et la confiance d'un rapprochement."""
    verdict = moteur.predire_un(_vers_enregistrement(entree))
    metriques.incrementer(f"verdict_{verdict['niveau_anomalie']}")
    metriques.incrementer(f"confiance_{verdict['confiance']['niveau']}")
    log.info(
        f"Prediction : {verdict['niveau_anomalie']} / confiance {verdict['confiance']['niveau']}",
        extra={
            "event": "prediction",
            "id_mutation": verdict["id_mutation"],
            "niveau_anomalie": verdict["niveau_anomalie"],
            "score_anomalie": verdict["score_anomalie"],
            "niveau_confiance": verdict["confiance"]["niveau"],
            "nb_motifs": len(verdict["motifs"]),
            "role_appelant": identite.role,
        },
    )
    return VerdictSortie(**verdict)


@app.post(
    "/predict/lot",
    response_model=LotSortie,
    tags=["prediction"],
    summary="Evaluer un lot de rapprochements",
)
def predict_lot(
    lot: LotEntree,
    identite: Annotated[Identite, Depends(exige_role("analyst"))],
    moteur: Annotated[Moteur, Depends(moteur_requis)],
) -> LotSortie:
    """Evaluation par lot, reservee au role `analyst`. Borne a 200 elements."""
    verdicts = [moteur.predire_un(_vers_enregistrement(e)) for e in lot.rapprochements]
    nb_eval = sum(1 for v in verdicts if v["statut"] == "evalue")
    metriques.incrementer("lots_traites")
    metriques.incrementer("rapprochements_traites", len(verdicts))
    log.info(
        f"Lot traite : {len(verdicts)} rapprochements",
        extra={"event": "prediction_lot", "taille": len(verdicts), "nb_evalues": nb_eval},
    )
    return LotSortie(
        resultats=[VerdictSortie(**v) for v in verdicts],
        nb_evalues=nb_eval,
        nb_non_evaluables=len(verdicts) - nb_eval,
    )


def _vers_enregistrement(entree: RapprochementEntree) -> dict[str, Any]:
    """Convertit le contrat d'API en enregistrement attendu par le moteur."""
    brut = entree.model_dump()
    brut["date_mutation"] = entree.date_mutation.isoformat()
    brut["date_dpe"] = entree.date_dpe.isoformat() if entree.date_dpe else None
    return brut


@app.exception_handler(Exception)
async def erreur_non_geree(request: Request, exc: Exception) -> JSONResponse:
    """Aucune trace interne ne fuit vers le client. (OWASP A05)"""
    log.error(
        f"Erreur non geree sur {request.url.path} : {exc}",
        extra={"event": "erreur_non_geree", "route": request.url.path,
               "erreur_type": type(exc).__name__},
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Erreur interne. L'identifiant de correlation permet le diagnostic."},
    )
