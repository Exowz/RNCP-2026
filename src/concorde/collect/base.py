"""Socle commun a toutes les collectes. (C1)

Le referentiel exige cinq **types** de sources : service web, page web, fichier,
base de donnees, systeme big data. Les rendre interchangeables suppose un
contrat unique. Chaque collecteur implemente `_collecter()` ; le socle se charge
du reste, identiquement pour tous :

- point d'entree unique et journalise ;
- gestion des erreurs qui n'interrompt pas la chaine mais la trace ;
- ecriture dans `data/raw/` sous un nom stable ;
- inscription au **manifeste** `data/raw/_manifest.json` : empreinte SHA-256,
  nombre de lignes, taille, horodatage, parametres d'appel.

Le manifeste est la preuve de C1 : il dit quoi a ete collecte, quand, d'ou, et
permet de verifier qu'un fichier n'a pas bouge depuis.
"""

from __future__ import annotations

import hashlib
import json
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import pandas as pd

from concorde.common.logging_setup import setup_logging
from concorde.common.paths import DATA_RAW

TypeSource = Literal["fichier", "service_web", "page_web", "base_de_donnees", "big_data"]

MANIFEST_PATH = DATA_RAW / "_manifest.json"


@dataclass(slots=True)
class ResultatCollecte:
    """Trace d'une collecte : ce qui a ete recupere, d'ou, et sous quelle forme."""

    nom: str
    type_source: TypeSource
    origine: str
    chemin: str
    nb_lignes: int
    octets: int
    sha256: str
    duree_s: float
    horodatage: str
    parametres: dict[str, Any] = field(default_factory=dict)
    succes: bool = True
    erreur: str | None = None


def sha256_fichier(chemin: Path, bloc: int = 1 << 20) -> str:
    """Empreinte SHA-256 d'un fichier, calculee par blocs."""
    digest = hashlib.sha256()
    with chemin.open("rb") as fh:
        while morceau := fh.read(bloc):
            digest.update(morceau)
    return digest.hexdigest()


def enregistrer_manifeste(resultat: ResultatCollecte) -> None:
    """Ajoute (ou remplace) l'entree du manifeste pour cette source."""
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    entrees: dict[str, dict] = {}
    if MANIFEST_PATH.exists():
        try:
            entrees = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            entrees = {}
    entrees[resultat.nom] = asdict(resultat)
    MANIFEST_PATH.write_text(
        json.dumps(entrees, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
    )


def lire_manifeste() -> dict[str, dict]:
    """Renvoie le manifeste courant (vide s'il n'existe pas)."""
    if not MANIFEST_PATH.exists():
        return {}
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


class Collecteur(ABC):
    """Contrat d'une source de donnees.

    Les sous-classes declarent `nom`, `type_source`, `origine` et implementent
    `_collecter()`, qui renvoie un DataFrame. Tout le reste est mutualise.
    """

    nom: str
    type_source: TypeSource
    origine: str
    #: Extension du fichier ecrit dans `data/raw/`.
    extension: str = "parquet"

    def __init__(self, destination: Path | None = None) -> None:
        self.destination = destination or DATA_RAW
        self.log = setup_logging("collect")

    @abstractmethod
    def _collecter(self) -> pd.DataFrame:
        """Recupere les donnees brutes. Peut lever : l'appelant gere."""

    @property
    def chemin_sortie(self) -> Path:
        return self.destination / f"{self.nom}.{self.extension}"

    def _ecrire(self, df: pd.DataFrame) -> Path:
        chemin = self.chemin_sortie
        chemin.parent.mkdir(parents=True, exist_ok=True)
        if self.extension == "parquet":
            df.to_parquet(chemin, index=False)
        elif self.extension == "csv":
            df.to_csv(chemin, index=False, encoding="utf-8")
        else:
            raise ValueError(f"Extension non geree : {self.extension}")
        return chemin

    def collecter(self, **parametres: Any) -> ResultatCollecte:
        """Point d'entree unique : collecte, ecrit, journalise, inscrit au manifeste.

        Une erreur ne remonte pas telle quelle : elle est journalisee et
        renvoyee dans un `ResultatCollecte` en echec, pour qu'une source
        indisponible n'interrompe pas la collecte des quatre autres.
        """
        debut = time.perf_counter()
        self.log.info(
            "Debut de collecte",
            extra={"event": "collecte_debut", "source": self.nom,
                   "type_source": self.type_source, "origine": self.origine},
        )
        try:
            df = self._collecter()
            chemin = self._ecrire(df)
            resultat = ResultatCollecte(
                nom=self.nom,
                type_source=self.type_source,
                origine=self.origine,
                chemin=str(chemin.relative_to(chemin.parents[2])),
                nb_lignes=len(df),
                octets=chemin.stat().st_size,
                sha256=sha256_fichier(chemin),
                duree_s=round(time.perf_counter() - debut, 3),
                horodatage=datetime.now(UTC).isoformat(),
                parametres=parametres,
            )
            self.log.info(
                f"Collecte reussie : {resultat.nb_lignes} lignes",
                extra={"event": "collecte_succes", "source": self.nom,
                       "nb_lignes": resultat.nb_lignes, "octets": resultat.octets,
                       "sha256": resultat.sha256[:16], "duree_s": resultat.duree_s},
            )
        except Exception as exc:  # noqa: BLE001 - une source en panne ne doit pas tout arreter
            resultat = ResultatCollecte(
                nom=self.nom,
                type_source=self.type_source,
                origine=self.origine,
                chemin="",
                nb_lignes=0,
                octets=0,
                sha256="",
                duree_s=round(time.perf_counter() - debut, 3),
                horodatage=datetime.now(UTC).isoformat(),
                parametres=parametres,
                succes=False,
                erreur=f"{type(exc).__name__}: {exc}",
            )
            self.log.error(
                f"Echec de collecte : {resultat.erreur}",
                extra={"event": "collecte_echec", "source": self.nom,
                       "erreur_type": type(exc).__name__},
                exc_info=True,
            )
        enregistrer_manifeste(resultat)
        return resultat
