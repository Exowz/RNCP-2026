# Preuve de livraison Docker — 24 août 2026

## Image locale préparée

La base `python:3.12-slim` a été préchargée, puis la construction suivante a
produit l'image locale `concorde:local` :

```bash
docker compose -f docker-compose.delivery.yml build --pull=false
```

Image obtenue :

```text
image=sha256:570b05aa7407ec2354e4c5840d6ce0a06e971f151fb3d498444bd842fe40efe3
size=3638068355 bytes
PYTHONPATH=/opt/concorde:/opt/concorde/src
```

La taille est une limite assumée de cette première image autonome : elle reprend
le graphe complet de la chaîne de validation pour garantir l'identité avec la
CI. Elle sera optimisée en image runtime séparée après l'évaluation, sans
masquer ce compromis le jour J.

## Préproduction sans build ni pull

Le port 8000 étant déjà pris par la session locale de développement, la même
composition a été exécutée temporairement sur 8011, sans build ni pull :

```bash
CONCORDE_DEMO_PORT=8011 \
  docker compose --project-name concorde-delivery-smoke \
  -f docker-compose.delivery.yml up -d --no-build
```

Résultat Compose :

```text
concorde-delivery-smoke-concorde-1  concorde:local  Up (healthy)
127.0.0.1:8011->8000/tcp
```

La sonde a répondu :

```json
{
  "statut": "ok",
  "service": "app",
  "api_modele_joignable": true,
  "api_modele": {"statut": "ok", "modele_charge": true, "hors_ligne": true},
  "hors_ligne": true
}
```

Enfin, `POST /evaluer` a affiché `Confiance elevee`. Les journaux app et API
partagent le `request_id` `da1136d589ee480aae371728d57fef71` :

```text
app       POST /evaluer -> 200 en 408.5 ms
api-model Prediction : normal / confiance eleve
api-model POST /predict -> 200 en 77.9 ms
```

La préproduction temporaire a ensuite été arrêtée avec `docker compose ... down`.
Cette preuve montre une livraison d'application réelle, locale, démarrée depuis
l'image déjà présente ; elle ne dépend pas d'un accès Internet au démarrage.
