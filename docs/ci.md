# CI du modele — C13

Le workflow [verify.yml](../.github/workflows/verify.yml) reproduit la chaine
sur Ubuntu : Java 17 pour Spark, PostgreSQL ephemere, installation verrouillee
par `uv.lock`, fixtures, collecte, nettoyage, entrainement, tests et lint.

Le test LM Studio porte le marqueur `local_service` : il n'est pas masque, mais
est exclu de la CI car celle-ci ne doit ni telecharger ni simuler le modele
personnel du poste. Il est execute dans la procedure C8 locale.

Pour prouver C18/C19, la prochaine etape est de publier ce depot vers GitHub,
declencher le workflow, puis archiver son URL et sa capture dans `reports/`.
