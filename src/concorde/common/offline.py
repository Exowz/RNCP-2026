"""Garde-fou hors ligne : la demo ne *promet* pas d'etre autonome, elle le *prouve*.

La contrainte d'examen est une demonstration sans Internet. Se contenter de
couper le Wi-Fi ne prouve rien au jury : une dependance cachee (telechargement
de poids, appel d'API, CDN) ne se revele qu'au pire moment.

Ce module installe un verrou au niveau de la couche socket : toute tentative de
connexion sortante vers autre chose que la boucle locale leve immediatement une
`OfflineViolation`, avec le nom de l'hote vise. Une dependance reseau oubliee
devient donc une erreur bruyante et localisee, pas une surprise en soutenance.

Le verrou laisse passer :
  - la boucle locale (127.0.0.0/8, ::1, `localhost`) : c'est ainsi que
    l'application parle a ses propres APIs (C10) ;
  - les sockets Unix : PostgreSQL en local, MLflow en magasin fichier.

Utilisation :
    from concorde.common.offline import enable_offline_guard
    enable_offline_guard()          # actif si CONCORDE_OFFLINE=true
    enable_offline_guard(force=True)  # actif quoi qu'il arrive (tests, demo)
"""

from __future__ import annotations

import ipaddress
import socket
from typing import Any

_LOOPBACK_NAMES = frozenset({"localhost", "localhost.localdomain", "ip6-localhost", ""})

_original_connect = socket.socket.connect
_original_connect_ex = socket.socket.connect_ex
_original_getaddrinfo = socket.getaddrinfo
_guard_installed = False


class OfflineViolation(RuntimeError):
    """Levee quand du code tente une connexion sortante en mode hors ligne."""


def _is_local(host: Any) -> bool:
    """Vrai si l'hote designe la machine elle-meme."""
    if not isinstance(host, str):
        return False
    name = host.strip("[]").lower()
    if name in _LOOPBACK_NAMES:
        return True
    try:
        return ipaddress.ip_address(name).is_loopback
    except ValueError:
        return False


def _check(address: Any, source: str) -> None:
    # Sockets Unix : l'adresse est un chemin, jamais un couple (hote, port).
    if not isinstance(address, tuple) or not address:
        return
    host = address[0]
    if _is_local(host):
        return
    raise OfflineViolation(
        f"Sortie reseau bloquee ({source}) vers {host!r}. "
        "La demonstration doit fonctionner hors ligne : la ressource doit etre "
        "presente localement avant l'execution. "
        "Mettre CONCORDE_OFFLINE=false pour autoriser la collecte en ligne."
    )


def enable_offline_guard(force: bool = False) -> bool:
    """Installe le verrou reseau. Renvoie True s'il est actif.

    Args:
        force: ignore la configuration et active le verrou dans tous les cas.
    """
    global _guard_installed

    if not force:
        from concorde.common.config import get_settings

        if not get_settings().offline:
            return False

    if _guard_installed:
        return True

    def guarded_connect(self: socket.socket, address: Any) -> Any:
        _check(address, "connect")
        return _original_connect(self, address)

    def guarded_connect_ex(self: socket.socket, address: Any) -> Any:
        _check(address, "connect_ex")
        return _original_connect_ex(self, address)

    def guarded_getaddrinfo(host: Any, port: Any, *args: Any, **kwargs: Any) -> Any:
        _check((host, port), "getaddrinfo")
        return _original_getaddrinfo(host, port, *args, **kwargs)

    socket.socket.connect = guarded_connect  # type: ignore[method-assign]
    socket.socket.connect_ex = guarded_connect_ex  # type: ignore[method-assign]
    socket.getaddrinfo = guarded_getaddrinfo  # type: ignore[assignment]
    _guard_installed = True
    return True


def disable_offline_guard() -> None:
    """Retire le verrou (collecte en ligne, tests d'integration reseau)."""
    global _guard_installed
    socket.socket.connect = _original_connect  # type: ignore[method-assign]
    socket.socket.connect_ex = _original_connect_ex  # type: ignore[method-assign]
    socket.getaddrinfo = _original_getaddrinfo  # type: ignore[assignment]
    _guard_installed = False


def is_guard_active() -> bool:
    """Indique si le verrou est actuellement installe."""
    return _guard_installed
