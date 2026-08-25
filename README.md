# Concorde — Secure MLOps immobilier

Concorde ne predit ni le prix d'un bien ni une tarification. Il evalue la
coherence d'un rapprochement DVF+ × DPE ADEME × Géorisques, son atypicite et le
niveau de confiance qui peut lui etre accorde.

> « Je ne remplace pas la decision ; je reduis l'ecart entre des donnees
> complexes et une decision informee, en rendant visibles les sources, les
> hypotheses et les inconnues. »

## Demonstration verticale hors ligne

La tranche demonstrable utilise uniquement les fixtures versionnees dans
`data/samples/`, un artefact PyTorch local et deux services locaux. Aucun poids
de modele, CDN ou appel d'API externe n'est necessaire.

```bash
# Dans le depot, avec les dependances deja installees dans .venv/.
# Java 17, PostgreSQL, l'import local, LM Studio et la suite complete sont verifies
# dans le meme environnement. LM Studio doit exposer google/gemma-4-e4b.
uv run python scripts/demarrer_demo.py

# La chaine peut ensuite etre montree separement.
.venv/bin/python -m concorde.collect
.venv/bin/python -m concorde.clean
.venv/bin/python -m concorde.model.entrainement

# Terminal 1 : API du modele, documentation locale :8002/docs
.venv/bin/uvicorn api.model.main:app --host 127.0.0.1 --port 8002

# Terminal 2 : application, puis ouvrir http://127.0.0.1:8000
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000

# Terminal 3 : preuve automatique et logs structures
curl --fail http://127.0.0.1:8000/sante
tail -n 5 monitoring/logs/app.jsonl
```

`demarrer_demo.py --ouvrir-lm-studio` ouvre LM Studio avant le controle ; le
modele reste a charger dans l'application si son serveur n'est pas deja pret.

Le garde-fou `CONCORDE_OFFLINE=true` est actif au demarrage de l'API et de
l'application : les connexions vers Internet echouent, mais `127.0.0.1` reste
autorise pour l'appel reel application → API. Les tests `tests/api/` et
`tests/app/` empechent une regression de ce contrat.

## Decisions defendables

- **Unite d'analyse** : le rapprochement candidat, pas le bien « vrai ». La
  parcelle est la cle commune ; les cas ambigus et sans DPE restent visibles.
- **Trois sorties separees** : coherence (regles explicables), anomalie
  (autoencodeur local) et confiance (donnees manquantes/ambiguite). Elles ne
  sont jamais fusionnees en une note opaque.
- **Demonstration stable** : une fixture a graine fixe reproduit les cas
  coherent, ecart de surface, DPE posterieur et absence de DPE ; elle ne se
  fait pas passer pour une collecte nationale.
- **Securite proportionnee** : cle API par role pour les services internes,
  validation stricte Pydantic et entetes HTTP ; aucun secret dans Git.

## Reperes de preuve

- [Matrice RNCP](reports/rncp/matrice-preuves.md) : etat reel des 21
  competences et emplacements des preuves.
- [E3](reports/rncp/E3.md), [E4](reports/rncp/E4.md), [E5](reports/rncp/E5.md)
  : paragraphes de preuve de la tranche verticale.
- `monitoring/logs/*.jsonl` : journaux structures correles par `request_id`.
- `reports/annexes/nettoyage_avant_apres.md` et
  `reports/annexes/metriques_modele.json` : sorties regenerables de la chaine.
- [Execution Spark DPE](docs/spark.md) : Java 17 epingle et preuve de lecture
  Spark locale.
- [Captures de soutenance](reports/captures/README.md) : ecrans d'accueil,
  evaluation et transparence obtenus sur l'application locale.
