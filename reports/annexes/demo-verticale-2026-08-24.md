# Preuve d'execution — tranche verticale du 24 aout 2026

## Commande de reproduction

```bash
.venv/bin/python -m pytest -q
.venv/bin/ruff check src api app tests
.venv/bin/python -m concorde.collect
.venv/bin/python -m concorde.clean
.venv/bin/python -m concorde.model.entrainement
.venv/bin/uvicorn api.model.main:app --host 127.0.0.1 --port 8002
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
curl --fail http://127.0.0.1:8000/sante
curl --fail -X POST http://127.0.0.1:8000/evaluer \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data 'profil=particulier&cas=coherent'
```

## Resultat observe

- Tests : `2 passed` ; controle statique : `All checks passed!`.
- Collecte locale : `3/3 sources, 1735 lignes`.
- Nettoyage : DVF `997 -> 900`, DPE `726 -> 689`, `922` rapprochements
  candidats et `77.7 %` avec DPE apparie.
- Entrainement local : `220 epoques`, meilleure perte de validation `0.22748`,
  artefact `models/concorde_moteur.pt` ecrit localement.
- Sante app : API modele joignable, modele charge, `hors_ligne: true`.
- Page particulier : le cas `coherent` affiche `Confiance elevee`.

## Extrait de journal correle

Le `request_id` `cecc6e15b6ea4ec1a5398d55429a183f` est present dans les deux
services, ce qui prouve l'appel HTTP reel application → API pour la meme
requete :

```json
{"component":"app","event":"acces_http","message":"POST /evaluer -> 200 en 81.0 ms","request_id":"cecc6e15b6ea4ec1a5398d55429a183f"}
{"component":"api-model","event":"acces_http","message":"POST /predict -> 200 en 21.6 ms","request_id":"cecc6e15b6ea4ec1a5398d55429a183f"}
```

Les tests de cycle de vie activent le verrou de sockets et verifient qu'une
resolution vers `example.org` leve `OfflineViolation` sans effectuer de requete
externe. Les appels `127.0.0.1` restent autorises, ce qui conserve cette chaine
demonstrable hors Internet.
