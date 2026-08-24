"""Application Concorde : deux lectures d'un meme rapprochement. (C10, C14, C17)

    uvicorn app.main:app --host 127.0.0.1 --port 8000

Deux publics, un seul moteur :

- **particulier** — ce que les donnees permettent reellement de savoir sur ce
  bien, et ce qu'elles ne permettent pas d'inferer. Phrases, pas de chiffres nus.
- **analyste** — variables, contributions, seuils, reserves. Les chiffres, avec
  ce qui les fabrique.

Le profil ne change **jamais** le calcul, seulement la restitution. Deux
utilisateurs voyant deux resultats differents sur la meme donnee serait un defaut
de conception, pas une fonctionnalite.

Rendu serveur en HTML, sans framework client et sans ressource distante : la page
fonctionne hors ligne, et le HTML produit est maitrise ligne a ligne, ce
qu'exigent les criteres d'accessibilite (C14, C17).
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Any
from urllib.parse import urlencode

from fastapi import FastAPI, Form, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.client import ClientModele, ErreurService
from app.exemples import charger as charger_exemples
from concorde.common.config import get_settings
from concorde.common.logging_setup import setup_logging
from concorde.common.offline import enable_offline_guard
from concorde.common.paths import MONITORING_APP
from concorde.service.observabilite import Metriques, ObservabiliteMiddleware
from concorde.service.securite import EntetesSecuriteMiddleware

SERVICE = "app"
BASE = Path(__file__).resolve().parent

log = setup_logging(SERVICE)
metriques = Metriques(SERVICE)


@asynccontextmanager
async def cycle_de_vie(app: FastAPI):
    """Verrouille les sorties reseau avant de servir la demo locale."""
    enable_offline_guard()
    yield
    metriques.deverser(MONITORING_APP / "metriques_app.json")


app = FastAPI(
    title="Concorde", docs_url=None, redoc_url=None, openapi_url=None, lifespan=cycle_de_vie
)
app.add_middleware(EntetesSecuriteMiddleware)
app.add_middleware(ObservabiliteMiddleware, service=SERVICE, metriques=metriques)
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")

gabarits = Jinja2Templates(directory=str(BASE / "templates"))
gabarits.env.filters["pourcent"] = lambda v: "—" if v is None else f"{float(v) * 100:.0f} %"

PROFILS = {"particulier": "Particulier", "analyste": "Analyste credit"}

LIBELLES_NIVEAU_ANOMALIE = {
    "normal": ("Conforme a ce qui est attendu", "ok"),
    "a_verifier": ("A verifier", "attention"),
    "atypique": ("Atypique", "alerte"),
    "non_evaluable": ("Non evaluable", "neutre"),
}
LIBELLES_CONFIANCE = {
    "eleve": ("Confiance elevee", "ok"),
    "moyen": ("Confiance moyenne", "attention"),
    "faible": ("Confiance faible", "alerte"),
    "insuffisant": ("Information insuffisante", "neutre"),
}
LIBELLES_ALEA = {0: "Nul", 1: "Tres faible", 2: "Faible", 3: "Moyen", 4: "Fort"}


def _liens_profil(request: Request, params_extra: dict[str, str] | None = None) -> dict[str, str]:
    """Construit, pour chaque profil, l'URL qui rejoue **la page courante** dans ce profil.

    Un simple `href="?profil=analyste"` renverrait un GET sur la page courante.
    Sur `/evaluer`, qui repond a un POST de formulaire, cela produisait un
    `405 Method Not Allowed` affiche en JSON brut : la bascule de profil, qui est
    pourtant la demonstration centrale (meme calcul, deux restitutions), cassait
    exactement la ou elle devait convaincre.

    Le lien reconstruit donc l'URL complete en conservant les parametres utiles
    (dont `cas`) et en ne remplacant que `profil`.
    """
    base = dict(request.query_params)
    base.pop("profil", None)
    base.update(params_extra or {})
    return {
        cle: f"{request.url.path}?{urlencode({**base, 'profil': cle})}" for cle in PROFILS
    }


def _contexte_commun(
    request: Request, profil: str, params_extra: dict[str, str] | None = None
) -> dict[str, Any]:
    return {
        "request": request,
        "profil": profil if profil in PROFILS else "particulier",
        "profils": PROFILS,
        "liens_profil": _liens_profil(request, params_extra),
        "exemples": charger_exemples(),
    }


@app.get("/", response_class=HTMLResponse, summary="Accueil")
def accueil(request: Request, profil: str = "particulier") -> HTMLResponse:
    return gabarits.TemplateResponse(
        request, "index.html", _contexte_commun(request, profil)
    )


@app.post("/evaluer", response_class=HTMLResponse, summary="Evaluer un rapprochement")
def evaluer(
    request: Request,
    profil: Annotated[str, Form()] = "particulier",
    cas: Annotated[str, Form()] = "coherent",
) -> HTMLResponse:
    """Soumission du formulaire de choix de cas."""
    return _rendre_evaluation(request, profil, cas)


@app.get("/evaluer", response_class=HTMLResponse, summary="Rejouer une evaluation")
def evaluer_get(
    request: Request,
    profil: Annotated[str, Query()] = "particulier",
    cas: Annotated[str, Query()] = "coherent",
) -> HTMLResponse:
    """Meme evaluation, atteignable en GET.

    Necessaire pour que la bascule de profil fonctionne depuis la page de
    resultat, et accessoirement pour qu'un resultat soit partageable par URL.
    L'evaluation est idempotente et sans effet de bord : elle relit une fixture
    et interroge l'API du modele, donc l'exposer en GET est legitime.
    """
    return _rendre_evaluation(request, profil, cas)


def _rendre_evaluation(request: Request, profil: str, cas: str) -> HTMLResponse:
    """Appelle l'API modele en HTTP et restitue le verdict selon le profil."""
    exemples = charger_exemples()
    contexte = _contexte_commun(request, profil, params_extra={"cas": cas})

    if cas not in exemples:
        contexte |= {
            "erreur_titre": "Cas de demonstration introuvable",
            "erreur_message": (
                "Le cas demande n'existe pas dans le jeu charge. Executez "
                "`python -m concorde.clean` pour reconstruire la table des rapprochements."
            ),
        }
        return gabarits.TemplateResponse(request, "erreur.html", contexte, status_code=404)

    charge = exemples[cas]["donnees"]
    try:
        verdict = ClientModele().evaluer(charge)
    except ErreurService as exc:
        log.warning(
            f"Evaluation impossible : {exc.detail_technique}",
            extra={"event": "evaluation_degradee", "statut_amont": exc.statut},
        )
        metriques.incrementer("evaluations_degradees")
        contexte |= {
            "erreur_titre": "Evaluation impossible",
            "erreur_message": exc.message_utilisateur,
        }
        return gabarits.TemplateResponse(request, "erreur.html", contexte, status_code=503)

    metriques.incrementer("evaluations_reussies")
    metriques.incrementer(f"profil_{contexte['profil']}")
    contexte |= {
        "cas": cas,
        "intitule_cas": exemples[cas]["intitule"],
        "entree": charge,
        "verdict": verdict,
        "libelle_anomalie": LIBELLES_NIVEAU_ANOMALIE[verdict["niveau_anomalie"]],
        "libelle_confiance": LIBELLES_CONFIANCE[verdict["confiance"]["niveau"]],
        "libelle_alea": LIBELLES_ALEA.get(verdict["exposition_aleas"]["niveau_max"], "Inconnu"),
    }
    return gabarits.TemplateResponse(request, "resultat.html", contexte)


@app.get("/transparence", response_class=HTMLResponse, summary="Modele et regles")
def transparence(request: Request, profil: str = "particulier") -> HTMLResponse:
    """Fiche du modele et catalogue des regles, tels que l'API les publie."""
    contexte = _contexte_commun(request, profil)
    try:
        client = ClientModele()
        contexte |= {"fiche": client.fiche_modele(), "regles": client.regles()}
    except ErreurService as exc:
        contexte |= {
            "erreur_titre": "Informations du modele indisponibles",
            "erreur_message": exc.message_utilisateur,
        }
        return gabarits.TemplateResponse(request, "erreur.html", contexte, status_code=503)
    return gabarits.TemplateResponse(request, "transparence.html", contexte)


@app.get("/exploitation", response_class=HTMLResponse, summary="Surveillance locale")
def exploitation(request: Request, profil: str = "particulier") -> HTMLResponse:
    """Restitue les compteurs, seuils et alertes locaux de l'application. (C20)"""
    contexte = _contexte_commun(request, profil)
    instantane = metriques.instantane()
    contexte |= {
        "instantane": instantane,
        "routes": sorted(instantane["routes"].items()),
        "alertes": instantane["alertes"],
    }
    return gabarits.TemplateResponse(request, "exploitation.html", contexte)


@app.get("/sante", summary="Etat de l'application et de son amont")
def sante() -> dict[str, Any]:
    """Sante de l'application **et** de l'API qu'elle consomme."""
    reglages = get_settings()
    try:
        amont = ClientModele().sante()
        joignable = True
    except ErreurService as exc:
        amont = {"erreur": exc.message_utilisateur}
        joignable = False
    metriques.deverser(MONITORING_APP / "metriques_app.json")
    return {
        "statut": "ok" if joignable and amont.get("statut") == "ok" else "degrade",
        "service": SERVICE,
        "api_modele_joignable": joignable,
        "api_modele": amont,
        "hors_ligne": reglages.offline,
    }
