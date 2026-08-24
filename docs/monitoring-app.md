# Monitorage applicatif — C20

## Ce qui est mesuré

Chaque requête de l'application et de l'API modèle traverse
`ObservabiliteMiddleware`. Il conserve en mémoire, par route : nombre d'appels,
erreurs 4xx/5xx, latences p50/p95/max et compteurs métier. Il ajoute ou propage
un `X-Request-ID` et écrit un journal JSONL structuré.

| Signal | Seuil | Alerte | Décision opérationnelle |
|---|---:|---|---|
| Latence p95 | > 750 ms | avertissement | Vérifier l'API modèle, la taille des lots et les logs corrélés. |
| Taux d'erreur | > 5 % | critique | Suspendre la démo de verdict, utiliser la page d'erreur explicite et diagnostiquer par `request_id`. |
| Santé amont | API modèle non joignable ou dégradée | état `degrade` sur `/sante` | Ne produire aucun résultat de substitution. |
| Dérive données | Rapport Evidently séparé | rapport HTML/JSON | Revoir la qualité du jeu avant ré-entraînement. |

Les alertes ne sont évaluées qu'après cinq appels sur une même route : c'est un
garde-fou contre une conclusion à partir d'un échantillon insignifiant.

## Restitution locale et preuves

La page `/exploitation` est le tableau de bord local de l'application. Elle
affiche les seuils, alertes actives et une table accessible par route. Les
instantanés sont également écrits dans `monitoring/app/metriques_app.json` à
l'arrêt ou sur `/sante`.

```bash
# Application déjà démarrée localement
curl --fail http://127.0.0.1:8000/exploitation
curl --fail http://127.0.0.1:8000/sante
tail -n 10 monitoring/logs/app.jsonl
tail -n 10 monitoring/logs/api-model.jsonl
```

Le `request_id` est la clé de diagnostic : l'annexe de livraison Docker montre
le même identifiant dans `POST /evaluer` (app) et `POST /predict` (API modèle).
Le test `test_tableau_de_bord_local_restitue_metriques_et_seuils` empêche la
disparition de cette restitution.

## RGPD et boucle MLOps

Les journaux n'écrivent ni clé API ni adresse IP en clair : le filtre de logs
pseudonymise ces valeurs avant disque. Les compteurs ne contiennent que route,
statut, durée et événements métier agrégés. La conservation est limitée à la
soutenance, comme indiqué dans le registre RGPD.

La boucle de retour est volontairement humaine : une alerte d'application
conduit à l'analyse des logs et à l'incident C21 ; une dérive Evidently conduit
à la revue des données et à un ré-entraînement validé par la CI. Concorde ne
déclenche jamais un ré-entraînement ou un déploiement automatiquement sur la
seule base d'une métrique.
