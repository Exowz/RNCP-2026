# CI du modele — C13

Le workflow [verify.yml](../.github/workflows/verify.yml) reproduit la chaine
sur Ubuntu : Java 17 pour Spark, PostgreSQL ephemere, installation verrouillee
par `uv.lock`, fixtures, collecte, nettoyage, entrainement, tests et lint.

Le test LM Studio porte le marqueur `local_service` : il n'est pas masque, mais
est exclu de la CI car celle-ci ne doit ni telecharger ni simuler le modele
personnel du poste. Il est execute dans la procedure C8 locale.

L'execution
[32772913151](https://github.com/Exowz/RNCP-2026/actions/runs/32772913151) a
effectivement passe sur GitHub le 24 aout 2026, sur le commit `23c5421` :
fixtures, PostgreSQL, collecte, nettoyage, entrainement, tests et lint. C'est
la preuve C18. Le dossier [d'incident C21](incident.md) documente les deux
echecs reels qui ont precede ce passage vert et leur non-regression.

La chaine de livraison de l'application (build/image, preproduction) reste le
prochain incrément C19 ; elle sera volontairement separee de cette preuve CI.
