# Secure MLOps — validation qualité, robustesse et sécurité d'un modèle IA

## Résumé exécutif

Concorde est une usine MLOps locale qui valide un moteur PyTorch d'anomalie, de cohérence et de confiance sur des rapprochements DVF+ × DPE × Géorisques. Il ne prédit ni prix ni tarif. La chaîne démontrée est : fixtures → collecte Spark et PostgreSQL → nettoyage → entraînement/évaluation → artefact gelé → API → tests → rapport de dérive → paquet Python → artefact GitHub → image Docker locale.

## Périmètre et critères de conformité

Le tableau ci-dessous décrit les axes couverts. Le **verdict**, lui, n'est pas rédigé : il est
**calculé**. `python scripts/conformite.py` évalue 12 critères sur ces trois axes, écrit
[`reports/annexes/conformite.md`](../annexes/conformite.md) — daté, généré, jamais édité à la main —
et **sort en code non nul** si un critère bloquant échoue. La CI l'exécute **avant** `uv build` :
aucun paquet n'est construit sur une chaîne non conforme.

| Axe | Contrôle automatisé | Preuve |
|---|---|---|
| Qualité données | Collecte, nettoyage, Spark SQL, PostgreSQL, tests de formats. | `tests/data/`, annexes avant/après. |
| Qualité modèle | Découpage train/val/test, métriques, test d'entraînement et rechargement. | `tests/model/test_entrainement.py`, fiche modèle. |
| Robustesse | Stabilité sous perturbation, bornes, champs optionnels, déterminisme et refus d'artefact absent. | `tests/model/test_robustesse.py`, tableau généré. |
| Sécurité | Clés par rôle, comparaison constante, CSP, secrets hors Git, audit Bandit et dépendances. | `docs/securite.md`, tableau généré. |
| Dérive | Rapport Evidently local sur variables DPE. | `scripts/monitor_model.py`, `docs/monitoring-modele.md`. |
| Livraison | **Porte de conformité bloquante avant build** (12 critères), CI GitHub, build roue/sdist, artefact modèle, image Docker locale. | [run 32857959387](https://github.com/Exowz/RNCP-2026/actions/runs/32857959387), `docs/livraison.md`. |

## Chaîne de validation

```bash
source scripts/spark-env.sh
uv run python scripts/import_postgres.py
uv run python -m concorde.collect
uv run python -m concorde.clean
uv run python -m concorde.model.entrainement
uv run pytest -m "not local_service"
uv run python scripts/monitor_model.py
uv run python scripts/conformite.py
uv build
```

La CI reproduit ces étapes sur Ubuntu, Java 17 et PostgreSQL éphémère. La porte produite dans `reports/annexes/conformite.{json,md}` décide avant le build ; elle n'est pas un tableau recopié à la main. La CI publie une roue, une archive source, le modèle gelé, sa fiche et ses métriques. Le test LM Studio est délibérément local : la CI ne télécharge pas de poids et ne simule pas le service du poste de démonstration.

## Gestion des incidents et décisions

**Cinq incidents réels** sont documentés dans [docs/incident.md](../../docs/incident.md), chacun avec reproduction, diagnostic, correctif minimal et non-régression vérifiée **dans les deux sens** — le correctif est retiré pour confirmer que le test échoue bien. Le dernier, `SEC-2026-08-25-bis`, porte sur la porte de conformité elle-même : elle déclarait conforme une chaîne d'entraînement cassée, parce qu'elle inspectait l'artefact sans rejouer le processus qui le produit. Un artefact valide ne prouve que le passé.

Le choix architectural essentiel est l'autonomie hors ligne : données, artefact, service IA, dépendances de démonstration et image Docker sont présents localement avant l'exécution. Le verrou socket rend toute sortie non locale bruyante.

## Limites et suite

La métrique de rappel des règles est circulaire sur le jeu de démonstration et ne prétend pas mesurer une performance nationale. L'image Docker autonome est lourde ; une image runtime minimale est l'amélioration prioritaire après l'évaluation. Aucune action de déploiement n'est prise automatiquement sur une alerte ou une dérive.
