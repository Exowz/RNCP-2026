# API modele — C9 et C12

L'API FastAPI locale expose le moteur gele `models/concorde_moteur.pt` sur
`http://127.0.0.1:8002/docs`. Les routes `/predict`, `/predict/lot`,
`/modele/fiche`, `/regles` et `/metriques` exigent `X-API-Key` selon le role.
`/sante` reste publique pour Docker et la CI.

```bash
curl --fail http://127.0.0.1:8002/predict \
  -H 'Content-Type: application/json' -H 'X-API-Key: dev-reader-key' \
  --data @payload.json
```

Les tests `tests/api/test_api_modele.py` prouvent les trois comportements
critiques : 401 sans cle, verdict valide avec cle reader, 422 pour champ non
attendu. Ils completent les tests de donnees, Spark, PostgreSQL et modele deja
present dans `tests/`.
