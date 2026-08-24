"""Point d'entree du nettoyage : `python -m concorde.clean`. (C3)"""

from __future__ import annotations

from concorde.clean.rapprochement import RAPPORT_MD, construire
from concorde.common.logging_setup import new_request_id, setup_logging
from concorde.common.paths import ensure_dirs


def main() -> int:
    ensure_dirs()
    log = setup_logging("clean")
    new_request_id()
    rappr, rapports = construire()
    for r in rapports:
        log.info(
            f"{r.jeu} : {r.lignes_initiales} -> {r.lignes_finales} "
            f"({r.lignes_supprimees} supprimees)",
            extra={"event": "bilan_nettoyage", "jeu": r.jeu,
                   "lignes_initiales": r.lignes_initiales,
                   "lignes_finales": r.lignes_finales},
        )
    log.info(f"Tableau avant/apres : {RAPPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
