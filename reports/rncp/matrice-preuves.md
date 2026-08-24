# Matrice de preuves RNCP

Legende : 🟢 prouve et reproductible · 🟡 amorce, preuve a completer · ⚪ non realise.

| Comp. | Etat | Preuve actuelle | Emplacement / commande |
|---|---|---|---|
| C1 | 🟢 | Six collecteurs rejouables : fichier, service web, page web, PostgreSQL et Spark. | `concorde.collect`, manifeste `data/raw/_manifest.json` |
| C2 | 🟢 | Jointure/filtres PostgreSQL et agregation Spark SQL executees et testees. | `docs/queries.md`, `tests/data/test_requetes_sql.py` |
| C3 | 🟢 | Nettoyage DVF/DPE, jointure et tableau avant/apres. | `python -m concorde.clean`, `reports/annexes/nettoyage_avant_apres.md` |
| C4 | 🟢 | MCD/MPD, PostgreSQL local, import idempotent et registre RGPD. | `docs/data-model.md`, `docs/rgpd.md`, `scripts/import_postgres.py` |
| C5 | 🟢 | API data REST authentifiee, OpenAPI et test de filtre. | `api/data/`, `docs/api-data.md`, `tests/api/test_api_data.py` |
| C6 | 🟡 | Veille datee, sources qualifiees et decisions ; limite individuel assumee. | `docs/veille.md` |
| C7 | 🟢 | Benchmark de services retenus/ecartes, dont sobriete et hors ligne. | `docs/benchmark.md` |
| C8 | 🟢 | LM Studio local, modele charge, acces HTTP, test et metriques. | `docs/service-ia.md`, `tests/model/test_lm_studio_service.py` |
| C9 | 🟢 | API modele authentifiee, OpenAPI et contrats d'entree/sortie testes. | `docs/api-modele.md`, `tests/api/test_api_modele.py` |
| C10 | 🟡 | Appel HTTP reel app → API, degradation prevue. | `app/`, [annexe demo](../annexes/demo-verticale-2026-08-24.md) |
| C11 | 🟢 | Metriques qualite, derive Evidently, latence/erreurs et alertes. | `docs/monitoring-modele.md`, `scripts/monitor_model.py` |
| C12 | 🟡 | Tests data, Spark, PostgreSQL, auth et contrat prediction ; couverture entrainement a completer. | `pytest -q`, `tests/` |
| C13 | 🟡 | Workflow CI execute : fixtures, collecte, entrainement, tests et lint ; packaging/livraison a finaliser. | `.github/workflows/verify.yml`, `docs/ci.md` |
| C14 | 🟢 | Personas, user stories, acceptation et exigences WCAG/RGAA explicites. | `docs/specs-fonctionnelles.md` |
| C15 | 🟢 | Architecture, flux, dependances, POC et contrainte hors ligne documentes. | `docs/architecture.md` |
| C16 | 🟡 | Pilotage individuel, tableau, Definition of Done, risques et REX ; limite collectif assumee. | `docs/pilotage.md` |
| C17 | 🟢 | Roles API, validation, CSP/entetes, secrets hors Git, pseudonymisation et accessibilite. | `docs/securite.md`, `tests/api/`, `app/templates/` |
| C18 | 🟢 | CI GitHub executee avec succes sur `23c5421`. | [run 32772913151](https://github.com/Exowz/RNCP-2026/actions/runs/32772913151), `docs/ci.md` |
| C19 | ⚪ | — | — |
| C20 | 🟡 | Logs JSONL, correlation et pseudonymisation. Dashboard/seuils a faire. | [annexe demo](../annexes/demo-verticale-2026-08-24.md) |
| C21 | 🟢 | Deux echecs CI reels, causes diagnostiquees, correctifs minimaux et execution verte de non-regression. | `docs/incident.md`, [run 32772913151](https://github.com/Exowz/RNCP-2026/actions/runs/32772913151) |

## Preuve de la tranche verticale — 24 aout 2026

La commande `python -m concorde.collect && python -m concorde.clean && python -m
concorde.model.entrainement` a produit 1 735 lignes brutes locales, 922
rapprochements candidats et l'artefact `models/concorde_moteur.pt`. L'application
locale a ensuite appele l'API modele en HTTP : les deux journaux partagent le
meme `request_id`, avec un `POST /predict` en 200. Cette preuve ne pretend pas
couvrir les cinq sources de C1 ni la CI : elle etablit le socle reproductible
sur lequel ces blocs seront ajoutes.
