# Monitoring modele — C11

Le monitoring combine trois niveaux complementaires :

1. qualite : metriques de test dans `reports/annexes/metriques_modele.json` ;
2. derive : rapport Evidently reference/lot courant ;
3. exploitation : latence, erreurs, compteurs et alertes dans `/metriques` de
   l'API modele.

```bash
.venv/bin/python scripts/monitor_model.py
open monitoring/model/evidently_drift.html
curl http://127.0.0.1:8002/metriques -H 'X-API-Key: dev-analyst-key'
```

Le rapport Evidently est entierement local et compare les variables d'entree
sur 70 % de reference contre 30 % de lot courant. Les seuils d'alerte HTTP sont
documentes dans `src/concorde/service/observabilite.py` : p95 au-dela de 750 ms
ou taux d'erreur au-dela de 5 %, apres cinq appels minimum.
