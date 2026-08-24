# CI du modele — C13

Le workflow [verify.yml](../.github/workflows/verify.yml) reproduit la chaine
sur Ubuntu : Java 17 pour Spark, PostgreSQL ephemere, installation verrouillee
par `uv.lock`, fixtures, collecte, nettoyage, entrainement, tests et lint.

Le test LM Studio porte le marqueur `local_service` : il n'est pas masque, mais
est exclu de la CI car celle-ci ne doit ni telecharger ni simuler le modele
personnel du poste. Il est execute dans la procedure C8 locale.

L'execution
[32777222782](https://github.com/Exowz/RNCP-2026/actions/runs/32777222782) a
effectivement passe sur GitHub le 24 aout 2026, sur le commit `78476b0` :
fixtures, PostgreSQL, collecte, nettoyage, entrainement, tests, lint,
construction de la distribution et upload de l'artefact
`concorde-livraison-78476b06ac8e5b39bf1eede618798a2660ce0875` (380 328 octets).
Il contient la roue et l'archive source, l'artefact PyTorch, la fiche de modele
et les metriques d'entrainement. C'est la preuve C13 et C18. Le dossier
[d'incident C21](incident.md) documente les deux echecs reels qui ont precede
le premier passage vert et leur non-regression.

La chaine de livraison de l'application (image Docker et preproduction locale)
est documentee et executee separement dans [livraison.md](livraison.md), pour
conserver une demonstration hors ligne independante de GitHub.
