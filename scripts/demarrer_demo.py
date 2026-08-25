#!/usr/bin/env python3
"""Prepare les prerequis locaux de la demonstration puis execute les tests."""

from __future__ import annotations

import argparse

from concorde.demo import PrevolDemoErreur, lancer_prevol


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ouvrir-lm-studio",
        action="store_true",
        help="ouvre LM Studio sur macOS avant le controle du serveur et du modele",
    )
    parser.add_argument(
        "--sans-tests",
        action="store_true",
        help="prepare les prerequis sans lancer pytest",
    )
    arguments = parser.parse_args()
    try:
        lancer_prevol(
            ouvrir_lm_studio=arguments.ouvrir_lm_studio,
            executer_tests=not arguments.sans_tests,
        )
    except PrevolDemoErreur as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
