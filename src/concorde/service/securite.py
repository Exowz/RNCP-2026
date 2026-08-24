"""Authentification, autorisation et durcissement HTTP. (C5, C9, C17)

Choix : **cle d'API portee par un en-tete `X-API-Key`**, associee a un role.

Pourquoi pas OAuth2 / JWT ? Les deux APIs de Concorde sont des services internes
appeles par une application de confiance et par la CI, pas par des utilisateurs
finaux authentifies individuellement. Un flux OAuth complet ajouterait un serveur
d'autorisation a maintenir et a demontrer hors ligne, pour un gain de securite
nul dans ce modele de menace. La cle d'API est le mecanisme proportionne — a
condition qu'il soit reellement applique, ce que les tests verifient.

Ce que le module garantit :

- aucune route metier n'est accessible sans cle valide (401) ;
- une cle valide mais de role insuffisant est refusee (403) ;
- la comparaison des cles est **a temps constant** (`secrets.compare_digest`),
  pour ne pas fuir la cle caractere par caractere via le temps de reponse ;
- les cles ne sont jamais journalisees en clair (le filtre RGPD les pseudonymise) ;
- les en-tetes de securite OWASP sont poses sur toutes les reponses.
"""

from __future__ import annotations

import secrets
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from concorde.common.config import ROLE_HIERARCHY, get_settings
from concorde.common.logging_setup import pseudonymize

NOM_ENTETE = "X-API-Key"

#: En-tetes de securite poses sur chaque reponse. Chacun repond a un risque
#: identifie de l'OWASP Top 10.
ENTETES_SECURITE: dict[str, str] = {
    # A03 Injection / XSS : interdit l'inference de type MIME par le navigateur.
    "X-Content-Type-Options": "nosniff",
    # A05 Mauvaise configuration : interdit l'inclusion en iframe (clickjacking).
    "X-Frame-Options": "DENY",
    # A01 Fuite d'information : ne transmet pas l'URL d'origine a un tiers.
    "Referrer-Policy": "no-referrer",
    # A03 XSS : aucune ressource distante, ce qui est aussi la contrainte hors ligne.
    "Content-Security-Policy": (
        "default-src 'self'; img-src 'self' data:; style-src 'self'; "
        "script-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'self'"
    ),
    # A05 : desactive des API navigateur inutiles au service.
    "Permissions-Policy": "geolocation=(), camera=(), microphone=(), payment=()",
    "Cache-Control": "no-store",
}


class Identite:
    """Identite de l'appelant, resolue a partir de sa cle d'API."""

    __slots__ = ("cle_pseudonymisee", "role")

    def __init__(self, role: str, cle_pseudonymisee: str) -> None:
        self.role = role
        self.cle_pseudonymisee = cle_pseudonymisee

    def a_le_role(self, minimum: str) -> bool:
        return ROLE_HIERARCHY[self.role] >= ROLE_HIERARCHY[minimum]

    def __repr__(self) -> str:  # pragma: no cover - confort de debogage
        return f"Identite(role={self.role!r})"


def resoudre_identite(
    x_api_key: Annotated[str | None, Header(alias=NOM_ENTETE)] = None,
) -> Identite:
    """Dependance FastAPI : verifie la cle d'API et renvoie l'identite associee."""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"En-tete {NOM_ENTETE} absent.",
            headers={"WWW-Authenticate": NOM_ENTETE},
        )

    table = get_settings().api_key_roles
    # Comparaison a temps constant sur toutes les cles connues : la duree de la
    # boucle ne depend pas de la position de la cle valide.
    role_trouve: str | None = None
    for cle_connue, role in table.items():
        if secrets.compare_digest(x_api_key, cle_connue):
            role_trouve = role

    if role_trouve is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cle d'API invalide.",
            headers={"WWW-Authenticate": NOM_ENTETE},
        )
    return Identite(role=role_trouve, cle_pseudonymisee=pseudonymize(x_api_key))


def exige_role(minimum: str):
    """Fabrique une dependance qui impose un role minimal."""
    if minimum not in ROLE_HIERARCHY:
        raise ValueError(f"Role inconnu : {minimum}")

    def verifier(identite: Annotated[Identite, Depends(resoudre_identite)]) -> Identite:
        if not identite.a_le_role(minimum):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{minimum}' requis ; role presente : '{identite.role}'.",
            )
        return identite

    return verifier


class EntetesSecuriteMiddleware(BaseHTTPMiddleware):
    """Pose les en-tetes de securite OWASP sur chaque reponse."""

    async def dispatch(self, request: Request, call_next) -> Response:
        reponse = await call_next(request)
        for nom, valeur in ENTETES_SECURITE.items():
            reponse.headers.setdefault(nom, valeur)
        return reponse
