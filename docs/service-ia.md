# Service IA local LM Studio — C8

Service retenu : LM Studio, API OpenAI-compatible liee a `127.0.0.1:1234`.
Modele : `google/gemma-4-e4b`, deja present localement. Le serveur est lie a la
boucle locale : seul l'utilisateur de la machine peut y acceder ; aucune donnee
Concorde n'est envoyee a Internet.

## Demarrage et verification

```bash
~/.lmstudio/bin/lms load google/gemma-4-e4b
~/.lmstudio/bin/lms server start
curl http://127.0.0.1:1234/v1/models
.venv/bin/python -m pytest tests/model/test_lm_studio_service.py -q
```

La configuration Concorde se trouve dans `.env.example` :

```dotenv
CONCORDE_LM_STUDIO_URL=http://127.0.0.1:1234/v1
CONCORDE_LM_STUDIO_MODEL=google/gemma-4-e4b
```

## Parametres et monitorage

Les appels explicatifs utiliseront `temperature=0` et une sortie token-bornee.
Avant tout appel, `ClientLMStudio.verifier_service()` exige le modele exact et
ecrit un evenement JSONL `service_ia_verifie` ainsi que
`monitoring/model/metriques_lm_studio.json`. En cas d'absence du serveur ou du
modele, il leve une erreur explicite : l'application doit afficher une
degradation, jamais inventer une explication.

Preuve observee le 24 aout : `POST /v1/chat/completions` a retourne
`SERVICE_LOCAL_OK` avec `finish_reason: stop` pour le modele retenu.
