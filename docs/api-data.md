# API data — C5

Demarrer PostgreSQL puis l'API :

```bash
docker compose up -d postgres
.venv/bin/python scripts/import_postgres.py
.venv/bin/uvicorn api.data.main:app --host 127.0.0.1 --port 8001
```

La specification est disponible localement sur `http://127.0.0.1:8001/docs`.

```bash
# Sans cle : 401
curl -i http://127.0.0.1:8001/communes?departement=33

# Avec cle reader : 200
curl --fail http://127.0.0.1:8001/communes?departement=33 \
  -H 'X-API-Key: dev-reader-key'
```

`GET /communes` valide le departement, applique une requete SQL parametree et
retourne le code INSEE, le nom communal, le niveau maximal et le nombre d'aleas
significatifs. Les exemples ci-dessus sont testes par
`tests/api/test_api_data.py`.
