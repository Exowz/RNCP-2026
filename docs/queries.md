# Requetes d'extraction — C2

## PostgreSQL : communes et exposition aux aleas

```sql
SELECT c.code_commune, c.nom_commune,
       COALESCE(MAX(a.niveau), 0) AS alea_max,
       COUNT(*) FILTER (WHERE a.niveau >= 3) AS nb_aleas_significatifs
FROM reference_commune AS c
LEFT JOIN exposition_alea AS a USING (code_commune)
WHERE c.departement = $1
GROUP BY c.code_commune, c.nom_commune
ORDER BY c.code_commune;
```

La requete preserve les communes sans alea (`LEFT JOIN`), filtre par
departement via la valeur parametree `$1` et s'appuie sur
`idx_reference_commune_departement`. L'index partiel
`idx_exposition_alea_niveau` sert aux futurs filtres de niveaux significatifs.

Preuve executee : `executer_requete_postgres("33")` retourne Bordeaux,
`alea_max = 3`, `nb_aleas_significatifs = 2`.

## Spark SQL : agregation DPE par commune

```sql
SELECT `Code_INSEE_(BAN)` AS code_commune,
       COUNT(*) AS nb_dpe,
       ROUND(AVG(CAST(`Conso_5_usages_par_m²_é_primaire` AS DOUBLE)), 2) AS conso_moyenne
FROM dpe
WHERE `Code_INSEE_(BAN)` IS NOT NULL
GROUP BY `Code_INSEE_(BAN)`
ORDER BY code_commune;
```

La lecture part du Parquet brut, evite la recreation d'un CSV et limite les
partitions de la demonstration a une (`spark.sql.shuffle.partitions=1`). La
requete produit trois communes et 726 DPE au total. Elle est executee par
`executer_requete_spark()` et testee dans `tests/data/test_requetes_sql.py`.

```bash
source scripts/spark-env.sh
.venv/bin/python scripts/import_postgres.py
.venv/bin/python -m pytest tests/data/test_requetes_sql.py -q
```
