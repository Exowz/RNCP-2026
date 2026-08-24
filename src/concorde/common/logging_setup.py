"""Journalisation structuree, unique pour toute la chaine. (C20, C21)

Trois exigences reunies dans un seul module :

1. **Exploitable par machine** : une ligne JSON par evenement (JSON Lines),
   ecrite dans `monitoring/logs/<composant>.jsonl`. On peut la filtrer avec
   `jq` sans parser du texte libre.
2. **Tracable de bout en bout** : un `request_id` porte par un `ContextVar`
   traverse l'application, l'appel HTTP a l'API et la prediction. Un incident
   se rejoue en filtrant sur cet identifiant. (C21)
3. **Conforme au RGPD** : un filtre de redaction masque les champs designes
   comme personnels *avant* l'ecriture sur disque. Le log ne doit jamais
   devenir un fichier de donnees personnelles parallele. (C20, C4)
"""

from __future__ import annotations

import contextvars
import hashlib
import json
import logging
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from concorde.common.paths import LOGS_DIR

# Identifiant de correlation propage dans toute la chaine (app -> API -> modele).
request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")

# Champs consideres comme donnees a caractere personnel ou quasi-identifiants.
# Ils sont pseudonymises (SHA-256 tronque) et jamais ecrits en clair. (RGPD)
SENSITIVE_FIELDS: frozenset[str] = frozenset(
    {
        "adresse",
        "address",
        "adresse_complete",
        "numero_voie",
        "nom",
        "prenom",
        "email",
        "telephone",
        "ip",
        "client_ip",
        "api_key",
        "password",
        "token",
        "authorization",
    }
)

# Attributs internes de LogRecord : tout le reste est considere comme un extra metier.
_RESERVED = frozenset(
    vars(logging.LogRecord("", 0, "", 0, "", (), None)).keys()
) | {"asctime", "message", "taskName"}


def pseudonymize(value: Any) -> str:
    """Pseudonymise une valeur : empreinte SHA-256 tronquee, non reversible.

    Permet de compter, correler et deduplique sans stocker la donnee elle-meme.
    """
    digest = hashlib.sha256(str(value).encode("utf-8")).hexdigest()
    return f"sha256:{digest[:16]}"


class RgpdRedactionFilter(logging.Filter):
    """Masque les champs personnels des `extra` avant serialisation. (C20 / RGPD)"""

    def filter(self, record: logging.LogRecord) -> bool:
        for key in list(vars(record).keys()):
            if key.lower() in SENSITIVE_FIELDS:
                setattr(record, key, pseudonymize(getattr(record, key)))
        return True


class JsonLinesFormatter(logging.Formatter):
    """Formate un enregistrement en une ligne JSON stable."""

    def __init__(self, component: str) -> None:
        super().__init__()
        self.component = component

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "component": self.component,
            "logger": record.name,
            "event": getattr(record, "event", record.funcName),
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
        }
        for key, value in vars(record).items():
            if key in _RESERVED or key in payload:
                continue
            try:
                json.dumps(value)
                payload[key] = value
            except (TypeError, ValueError):
                payload[key] = repr(value)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


class HumanFormatter(logging.Formatter):
    """Format lisible a l'ecran, pour la demo devant le jury."""

    def format(self, record: logging.LogRecord) -> str:
        rid = request_id_var.get()
        rid_part = f" [{rid[:8]}]" if rid != "-" else ""
        event = getattr(record, "event", "")
        event_part = f" <{event}>" if event else ""
        ts = datetime.fromtimestamp(record.created, tz=UTC).strftime("%H:%M:%S")
        return f"{ts} {record.levelname:<7}{rid_part}{event_part} {record.getMessage()}"


def setup_logging(
    component: str,
    level: str = "INFO",
    log_dir: Path | None = None,
    console: bool = True,
) -> logging.Logger:
    """Configure la journalisation pour un composant et renvoie son logger.

    Args:
        component: nom court du composant (`collect`, `api-model`, `app`...).
            Determine le nom du fichier `monitoring/logs/<component>.jsonl`.
        level: niveau minimal (`DEBUG`, `INFO`, `WARNING`...).
        log_dir: repertoire de sortie ; `monitoring/logs` par defaut.
        console: si vrai, duplique les messages a l'ecran en format lisible.

    Returns:
        Le logger nomme `concorde.<component>`.
    """
    directory = log_dir or LOGS_DIR
    directory.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger("concorde")
    root.setLevel(level.upper())
    # Idempotent : une seconde configuration ne duplique pas les handlers.
    for handler in list(root.handlers):
        root.removeHandler(handler)
        handler.close()

    redaction = RgpdRedactionFilter()

    file_handler = logging.FileHandler(directory / f"{component}.jsonl", encoding="utf-8")
    file_handler.setFormatter(JsonLinesFormatter(component))
    file_handler.addFilter(redaction)
    root.addHandler(file_handler)

    if console:
        stream = logging.StreamHandler(sys.stderr)
        stream.setFormatter(HumanFormatter())
        stream.addFilter(redaction)
        root.addHandler(stream)

    root.propagate = False
    return logging.getLogger(f"concorde.{component}")


def new_request_id() -> str:
    """Genere et installe un nouvel identifiant de correlation."""
    rid = uuid.uuid4().hex
    request_id_var.set(rid)
    return rid
