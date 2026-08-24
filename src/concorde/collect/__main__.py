"""Point d'entree de la collecte. (C1)

    python -m concorde.collect            # toutes les sources disponibles
    python -m concorde.collect dvf dpe    # un sous-ensemble

Renvoie un code de sortie non nul si au moins une source a echoue, pour que la
CI puisse s'appuyer dessus.
"""

from __future__ import annotations

import sys

from concorde.collect.base import Collecteur
from concorde.collect.fichier import CollecteurAleas, CollecteurDPE, CollecteurDVF
from concorde.common.logging_setup import new_request_id, setup_logging
from concorde.common.paths import ensure_dirs

COLLECTEURS: dict[str, type[Collecteur]] = {
    "dvf": CollecteurDVF,
    "dpe": CollecteurDPE,
    "aleas": CollecteurAleas,
}


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    ensure_dirs()
    log = setup_logging("collect")
    new_request_id()

    demandes = argv or list(COLLECTEURS)
    inconnues = [n for n in demandes if n not in COLLECTEURS]
    if inconnues:
        log.error(f"Sources inconnues : {inconnues}. Disponibles : {list(COLLECTEURS)}")
        return 2

    resultats = [COLLECTEURS[nom]().collecter(mode="samples") for nom in demandes]
    echecs = [r for r in resultats if not r.succes]

    total_lignes = sum(r.nb_lignes for r in resultats)
    log.info(
        f"Collecte terminee : {len(resultats) - len(echecs)}/{len(resultats)} sources, "
        f"{total_lignes} lignes",
        extra={"event": "collecte_bilan", "nb_sources": len(resultats),
               "nb_echecs": len(echecs), "total_lignes": total_lignes},
    )
    return 1 if echecs else 0


if __name__ == "__main__":
    raise SystemExit(main())
