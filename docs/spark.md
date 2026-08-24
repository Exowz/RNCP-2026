# Spark DPE — preuve et environnement local

## Decision technique

Les DPE ADEME sont la source « systeme big data ». La demonstration ne tente
pas de cloner l'historique national : elle lit son extrait versionne par une
vraie session Spark locale (`local[1]`), puis transforme la sortie en table
Parquet de la chaine. Le chemin d'execution est donc le meme (Spark) sans le
volume ni la dependance reseau.

## Precondition JDK

PySpark 3.5.9 embarque Hadoop 3.3.x. Ce couple utilise encore
`javax.security.auth.Subject.getSubject`, retire par le JDK 26 du poste. Java
17 est donc epingle pour Spark ; ce n'est pas un detail de machine mais une
contrainte de reproductibilite a declarer aussi dans la CI.

```bash
source scripts/spark-env.sh
.venv/bin/python -m pytest tests/data/test_collecte_dpe_spark.py -q
.venv/bin/python -m concorde.collect dpe
```

Resultat attendu : le test valide les 726 lignes et les colonnes ADEME
indispensables. La collecte inscrit ensuite `dpe` avec `type_source:
"big_data"` dans `data/raw/_manifest.json`.

## Limite assumee

L'extrait est une fixture de demonstration, non un echantillon representatif du
parc francais. Son objectif est de prouver le pipeline et les regles, jamais de
generaliser une performance statistique.
