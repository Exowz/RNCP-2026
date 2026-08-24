# Matrice de preuves RNCP

Legende : 🟢 prouve et reproductible · 🟡 amorce, preuve a completer · ⚪ non realise.

| Comp. | Etat | Preuve actuelle | Emplacement / commande |
|---|---|---|---|
| C1 | 🟡 | Trois fixtures locales collectees ; les cinq types de sources restent a faire. | `python -m concorde.collect`, `monitoring/logs/collect.jsonl` |
| C2 | ⚪ | — | — |
| C3 | 🟢 | Nettoyage DVF/DPE, jointure et tableau avant/apres. | `python -m concorde.clean`, `reports/annexes/nettoyage_avant_apres.md` |
| C4 | ⚪ | — | — |
| C5 | ⚪ | — | — |
| C6 | ⚪ | — | — |
| C7 | ⚪ | — | — |
| C8 | ⚪ | — | — |
| C9 | 🟡 | API modele locale, contrats Pydantic, OpenAPI et roles ; tests metier a completer. | `api/model/`, `http://127.0.0.1:8002/docs` |
| C10 | 🟡 | Appel HTTP reel app → API, degradation prevue. | `app/`, [annexe demo](../annexes/demo-verticale-2026-08-24.md) |
| C11 | 🟡 | Compteurs et latence JSON ; rapport Evidently et alertes restent a faire. | `monitoring/model/` |
| C12 | 🟡 | Deux tests d'integration du contrat hors ligne ; couverture modele a construire. | `pytest -q`, `tests/` |
| C13 | 🟡 | Chaine locale collecte → nettoyage → entrainement → artefact. CI et packaging a faire. | commandes README |
| C14 | ⚪ | — | — |
| C15 | ⚪ | — | — |
| C16 | 🟡 | Journal de decisions individuel existe ; backlog et retrospective a faire. | `docs/journal-decisions.md` |
| C17 | 🟡 | Authentification par cle et entetes de securite implementes ; preuve de test a completer. | `src/concorde/service/securite.py` |
| C18 | ⚪ | — | — |
| C19 | ⚪ | — | — |
| C20 | 🟡 | Logs JSONL, correlation et pseudonymisation. Dashboard/seuils a faire. | [annexe demo](../annexes/demo-verticale-2026-08-24.md) |
| C21 | ⚪ | Incident reel, correctif et non-regression a provoquer demain. | — |

## Preuve de la tranche verticale — 24 aout 2026

La commande `python -m concorde.collect && python -m concorde.clean && python -m
concorde.model.entrainement` a produit 1 735 lignes brutes locales, 922
rapprochements candidats et l'artefact `models/concorde_moteur.pt`. L'application
locale a ensuite appele l'API modele en HTTP : les deux journaux partagent le
meme `request_id`, avec un `POST /predict` en 200. Cette preuve ne pretend pas
couvrir les cinq sources de C1 ni la CI : elle etablit le socle reproductible
sur lequel ces blocs seront ajoutes.
