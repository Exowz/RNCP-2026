"""API REST des donnees preparees pour Concorde. (C5)"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Query

from concorde.common.offline import enable_offline_guard
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
