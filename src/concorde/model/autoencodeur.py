"""Detecteur d'anomalie : auto-encodeur tabulaire PyTorch.

Pourquoi un auto-encodeur, et pas une classification ?

Il n'existe pas d'etiquette « ce rapprochement est faux » dans les donnees
publiques : personne n'a annote les appariements DVF x DPE. Le probleme est donc
non supervise par nature. L'auto-encodeur apprend a reconstruire la structure
majoritaire des rapprochements ; ce qu'il reconstruit mal est, par construction,
ce qui ne ressemble pas au reste.

Pourquoi pas un IsolationForest, plus simple ? Deux raisons defendables :
le referentiel du projet n°21 impose PyTorch dans la chaine ; et l'erreur de
reconstruction est decomposable **par variable**, ce qui permet de dire a
l'utilisateur *quelle* dimension est atypique, pas seulement que la ligne l'est.
C'est la meme exigence d'explicabilite que pour la couche de regles.

Le score brut est une erreur quadratique, non bornee et non interpretable. Il est
calibre en rang par rapport a la distribution d'entrainement : le score final est
le percentile de l'erreur, dans [0, 1]. « 0,97 » se lit alors « plus atypique que
97 % du jeu d'apprentissage » — une phrase qui tient devant un jury.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from torch import nn

GRAINE = 20260824


class AutoEncodeur(nn.Module):
    """Auto-encodeur dense, volontairement petit.

    Le jeu compte quelques milliers de lignes et huit variables : un reseau plus
    large memoriserait les anomalies au lieu de les manquer, ce qui reduirait
    l'erreur de reconstruction sur les lignes qu'on cherche precisement a isoler.
    Le goulot (`dim_latente`) est le parametre qui force la generalisation.
    """

    def __init__(self, dim_entree: int, dim_cachee: int = 12, dim_latente: int = 3) -> None:
        super().__init__()
        self.dim_entree = dim_entree
        self.encodeur = nn.Sequential(
            nn.Linear(dim_entree, dim_cachee),
            nn.ReLU(),
            nn.Linear(dim_cachee, dim_latente),
        )
        self.decodeur = nn.Sequential(
            nn.Linear(dim_latente, dim_cachee),
            nn.ReLU(),
            nn.Linear(dim_cachee, dim_entree),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.decodeur(self.encodeur(x))


@dataclass(slots=True)
class HistoriqueEntrainement:
    perte_entrainement: list[float]
    perte_validation: list[float]

    @property
    def meilleure_perte_validation(self) -> float:
        return min(self.perte_validation) if self.perte_validation else float("nan")


def erreurs_par_variable(modele: AutoEncodeur, x: np.ndarray) -> np.ndarray:
    """Erreur quadratique de reconstruction, variable par variable."""
    modele.eval()
    with torch.no_grad():
        tenseur = torch.from_numpy(np.asarray(x, dtype=np.float32))
        reconstruit = modele(tenseur)
        return ((tenseur - reconstruit) ** 2).numpy()


def erreurs(modele: AutoEncodeur, x: np.ndarray) -> np.ndarray:
    """Erreur de reconstruction agregee (moyenne sur les variables)."""
    return erreurs_par_variable(modele, x).mean(axis=1)


def entrainer(
    x_train: np.ndarray,
    x_val: np.ndarray,
    dim_cachee: int = 12,
    dim_latente: int = 3,
    epoques: int = 220,
    taille_lot: int = 64,
    taux: float = 1e-3,
    patience: int = 25,
    graine: int = GRAINE,
) -> tuple[AutoEncodeur, HistoriqueEntrainement]:
    """Entraine l'auto-encodeur avec arret anticipe sur la perte de validation.

    L'arret anticipe n'est pas cosmetique : un auto-encodeur entraine trop
    longtemps finit par reconstruire correctement les anomalies elles-memes,
    et le detecteur perd sa raison d'etre.
    """
    torch.manual_seed(graine)
    np.random.seed(graine)

    modele = AutoEncodeur(x_train.shape[1], dim_cachee=dim_cachee, dim_latente=dim_latente)
    optimiseur = torch.optim.Adam(modele.parameters(), lr=taux)
    critere = nn.MSELoss()

    t_train = torch.from_numpy(np.asarray(x_train, dtype=np.float32))
    t_val = torch.from_numpy(np.asarray(x_val, dtype=np.float32))
    chargeur = torch.utils.data.DataLoader(
        torch.utils.data.TensorDataset(t_train),
        batch_size=taille_lot,
        shuffle=True,
        generator=torch.Generator().manual_seed(graine),
    )

    historique = HistoriqueEntrainement([], [])
    meilleure = float("inf")
    meilleurs_poids = {k: v.clone() for k, v in modele.state_dict().items()}
    sans_progres = 0

    for _ in range(epoques):
        modele.train()
        cumul = 0.0
        for (lot,) in chargeur:
            optimiseur.zero_grad()
            perte = critere(modele(lot), lot)
            perte.backward()
            optimiseur.step()
            cumul += perte.item() * len(lot)
        perte_train = cumul / len(t_train)

        modele.eval()
        with torch.no_grad():
            perte_val = critere(modele(t_val), t_val).item()

        historique.perte_entrainement.append(perte_train)
        historique.perte_validation.append(perte_val)

        if perte_val < meilleure - 1e-6:
            meilleure = perte_val
            meilleurs_poids = {k: v.clone() for k, v in modele.state_dict().items()}
            sans_progres = 0
        else:
            sans_progres += 1
            if sans_progres >= patience:
                break

    modele.load_state_dict(meilleurs_poids)
    return modele, historique
