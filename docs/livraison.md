# Livraison locale de l'application — C19

## Décision de livraison

L'image `concorde:local` livre l'application et l'API modèle dans un seul
conteneur. L'appel application → API reste un appel HTTP réel sur
`127.0.0.1:8002`, mais aucun réseau Docker ni service externe n'est nécessaire.
Le seul port publié est `127.0.0.1:8000` : l'application est visible depuis le
poste de démonstration, pas depuis le réseau local.

Les fixtures, le parquet traité et `models/concorde_moteur.pt` sont copiés dans
l'image au build. Le démarrage ne collecte pas, n'entraîne pas et ne télécharge
aucun modèle.

Cette première image autonome reprend le graphe de dépendances verrouillé de la
chaîne, y compris les outils MLOps. C'est volontairement plus lourd qu'une
image de serving minimaliste, mais garantit ce soir l'identité entre CI et
préproduction. Une image runtime réduite (sans Spark, DVC, MLflow ni Evidently)
est une optimisation identifiée, pas une propriété revendiquée de cette release.

## Préparation connectée — à faire avant la démo

```bash
# Base Python déjà préchargée localement, puis construction de l'image de release
docker pull python:3.12-slim
docker compose -f docker-compose.delivery.yml build
```

Cette étape est volontairement séparée : elle produit l'image locale
`concorde:local`. Elle peut être vérifiée avant de couper Internet.

## Préproduction et démonstration hors ligne

```bash
# Aucun build et aucun pull : l'image locale doit déjà exister.
docker compose -f docker-compose.delivery.yml up -d --no-build
docker compose -f docker-compose.delivery.yml ps
curl --fail http://127.0.0.1:8000/sante
open http://127.0.0.1:8000

# Après la démonstration
docker compose -f docker-compose.delivery.yml down
```

`pull_policy: never`, `--no-build` et le garde-fou socket des services rendent
un téléchargement ou un appel Internet impossible au démarrage. Si l'image ou
l'artefact manque, la livraison échoue explicitement avant ou pendant la sonde ;
elle ne bascule pas vers une dépendance distante.

## Vérification de release

La preuve C19 est un build local suivi d'un démarrage, d'une sonde `/sante` et
d'une évaluation dans le navigateur. La commande exacte et le résultat daté
sont conservés dans `reports/annexes/` après l'exécution. Le workflow GitHub
complète cette livraison avec le packaging Python de C13 ; il ne construit pas
l'image de démo, car la contrainte d'examen exige que celle-ci soit déjà locale.
