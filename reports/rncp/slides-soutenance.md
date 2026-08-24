# Conducteur de soutenance RNCP — 12 slides

1. **Concorde : rendre les inconnues visibles** — problème, ligne de défense, pas de prix/tarif. *Preuves : C1–C21.*
2. **Deux publics, une même décision** — particulier / analyste ; le profil change l'explication, jamais le calcul. *C14, C17.*
3. **Architecture hors ligne** — données → modèle → API → app → logs ; montrer `docs/architecture.md`. *C15.*
4. **C1–C5 : données rejouables** — six collecteurs, Spark DPE, PostgreSQL, API data ; montrer manifeste ou OpenAPI.
5. **C6–C8 : service IA local proportionné** — benchmark, LM Studio, rôle limité au texte ; annoncer honnêtement C6 partiel.
6. **C9–C13 : modèle livré** — trois sorties séparées, API auth, tests, Evidently, artefact GitHub ; montrer run vert.
7. **Démo : un cas cohérent** — choisir `coherent`, verdict et réserves ; montrer l'appel HTTP réel.
8. **Démo : un cas qui ne conclut pas** — choisir `sans_dpe`, expliquer confiance et non-évaluation.
9. **C14–C17 : application accessible et sûre** — lien d'évitement, focus, aria-live, CSP, rôles API.
10. **C18–C19 : CI et livraison locale** — run GitHub + image `concorde:local`, `--no-build`, sonde healthy.
11. **C20–C21 : monitorage et incident réel** — `/exploitation`, request_id, deux échecs CI et correctifs.
12. **Bilan et limites** — C6/C16 partiels par honnêteté ; jeu démo non national ; améliorations.

## Démo courte reproductible

```bash
source scripts/spark-env.sh
uv run python -m concorde.collect && uv run python -m concorde.clean
uv run python -m concorde.model.entrainement
uv run uvicorn api.model.main:app --host 127.0.0.1 --port 8002
# second terminal
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Ouvrir `http://127.0.0.1:8000`, puis `/exploitation`. En démo Docker, utiliser `docker compose -f docker-compose.delivery.yml up -d --no-build`.
