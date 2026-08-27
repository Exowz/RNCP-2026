# Matrice de preuves RNCP — Concorde

Mise à jour : 25 août 2026. Légende : 🟢 prouvé et reproductible · 🟡 partiel, limite assumée · ⚪ non réalisé.

**Aucune compétence n'est au statut « on l'a fait ».** Chaque ligne renvoie à un chemin Git,
une commande de reproduction ou un résultat vérifiable.

## Chiffres de référence

| Indicateur | Valeur |
|---|---|
| Tests automatisés | **54**, couverture **86 %** — **52** et **85 %** dans la porte, qui écarte le service local |
| Types de sources collectées | **5** exigés, 6 collecteurs |
| Rapprochements produits | **922** — 716 appariés, **206 non évaluables assumés** |
| Pouvoir discriminant du modèle | **AUC 0,9095** (auto-encodeur seul) |
| Porte de conformité | **12 critères** bloquants sur 3 axes |
| Incidents réels documentés | **5**, tous avec reproduction et non-régression |
| Captures disponibles | **16** |
| Dernière CI verte | [32857959387](https://github.com/Exowz/RNCP-2026/actions/runs/32857959387) |

---

## Bloc 1 — Collecter, stocker, mettre à disposition (C1–C5)

| Comp. | État | Preuve | Où / commande |
|---|---|---|---|
| **C1** | 🟢 | Six collecteurs couvrant les **cinq types exigés** : fichier (DVF), big data (DPE via Spark), service web (BAN), page web (Géorisques), base de données (PostgreSQL). Manifeste horodaté avec empreinte SHA-256, volumes et statut par source. | `python -m concorde.collect` → `data/raw/_manifest.json` |
| **C2** | 🟢 | Requêtes **PostgreSQL** (jointure communes × aléas) **et Spark SQL** (agrégation DPE par commune), documentées et testées. | `docs/queries.md`, `tests/data/test_requetes_sql.py` |
| **C3** | 🟢 | 10 règles de nettoyage nommées et **justifiées**, chacune comptant les lignes qu'elle supprime. Tableau avant/après **généré**, jamais recopié. Dataset **versionné par DVC**. | `python -m concorde.clean` → `reports/annexes/nettoyage_avant_apres.md` · `data/processed/rapprochements.parquet.dvc` |
| **C4** | 🟢 | MCD, MPD, PostgreSQL 17 conteneurisé, import idempotent, registre RGPD dont l'engagement de minimisation est **vérifié par un test**. | `docs/data-model.md`, `docs/rgpd.md`, `scripts/import_postgres.py` |
| **C5** | 🟢 | API REST authentifiée par rôle : `/communes`, `/rapprochements`, `/rapprochements/{id}`, `/rapprochements/demonstration`. OpenAPI générée depuis le contrat appliqué. | `api/data/`, `docs/api-data.md`, `tests/api/test_api_data.py` |

**À montrer** : le manifeste (5 types), le tableau avant/après (chaque règle supprime des lignes),
le test qui interdit la publication d'une adresse.

## Bloc 2 — Modèles et services IA, API, MLOps (C6–C13)

| Comp. | État | Preuve | Où / commande |
|---|---|---|---|
| **C6** | 🟡 | Veille datée, sources qualifiées, décisions tracées. **Limite assumée** : candidat seul, aucun collectif à animer ni à simuler. | `docs/veille.md` |
| **C7** | 🟢 | Benchmark de services IA **retenus et écartés**, critères incluant sobriété et fonctionnement hors ligne. | `docs/benchmark.md` |
| **C8** | 🟢 | LM Studio local, modèle `gemma-4-e4b` **présent sur disque (6,4 Go)**, accès HTTP, métriques et test dédié. | `docs/service-ia.md`, `tests/model/test_lm_studio_service.py` |
| **C9** | 🟢 | `/predict` : authentification par rôle, validation Pydantic stricte (`extra="forbid"`), OpenAPI, trois sorties **jamais fusionnées**. | `api/model/`, `docs/api-modele.md` |
| **C10** | 🟢 | **Deux clients indépendants** consomment la même API en HTTP : application Jinja (`:8000`) et front Next.js (`:3000`). Dégradation propre quand l'API tombe. | `app/`, `app/web/`, capture `09-web-degradation-api-indisponible.jpg` |
| **C11** | 🟢 | Evidently (dérive), métriques de latence et d'erreur par route, seuils et alertes. | `scripts/monitor_model.py`, `monitoring/model/`, `docs/monitoring-modele.md` |
| **C12** | 🟢 | **54 tests**, couverture **86 %** : formats, nettoyage, Spark, PostgreSQL, entraînement, rechargement d'artefact, endpoints, **robustesse du modèle**, accessibilité. | `pytest -m "not local_service"` |
| **C13** | 🟢 | Chaîne complète exécutée en CI : fixtures → PostgreSQL → collecte → nettoyage → **entraînement** → tests → sécurité → **porte de conformité** → build → artefact. | [run 32857959387](https://github.com/Exowz/RNCP-2026/actions/runs/32857959387), `docs/ci.md` |

**À montrer** : les trois axes séparés sur un cas, la fiche de modèle avec ses **limites assumées**,
le run CI vert avec toutes ses étapes.

## Bloc 3 — Application, CI/CD, MCO (C14–C21)

| Comp. | État | Preuve | Où / commande |
|---|---|---|---|
| **C14** | 🟢 | Personas, user stories, critères d'acceptation, exigences WCAG/RGAA explicites. Deux profils de restitution — **le profil change l'explication, jamais le calcul**. | `docs/specs-fonctionnelles.md`, `docs/specs-frontend-web.md` |
| **C15** | 🟢 | Architecture, flux, dépendances, contrainte hors ligne. Chaîne avec volumes réels restituée dans l'application. | `docs/architecture.md`, page « Comment ça marche » |
| **C16** | 🟡 | Pilotage individuel : kanban, journal de décisions daté, définition de « terminé », rétrospective. **Limite assumée** : pas de rituels collectifs. Le volet **MLOps** de C16 est en revanche entièrement couvert. | `docs/pilotage.md`, `docs/journal-decisions.md` |
| **C17** | 🟢 | Rôles par clé d'API, comparaison à temps constant, validation stricte, en-têtes OWASP, secrets hors Git, journaux pseudonymisés, **clé d'API jamais exposée au navigateur** (`server-only`). Contrastes calculés ≥ 4,5:1 en clair **et** en sombre. | `docs/securite.md`, `src/concorde/service/securite.py`, `app/web/lib/concorde.ts` |
| **C18** | 🟢 | CI GitHub réellement exécutée. Analyse statique **Bandit** et audit de dépendances **pip-audit** intégrés. | [run 32857959387](https://github.com/Exowz/RNCP-2026/actions/runs/32857959387) |
| **C19** | 🟢 | Image Docker locale, démarrage Compose `--no-build`, sonde saine. **La porte de conformité bloque le build** si un critère échoue : la livraison est conditionnelle, pas automatique. | `Dockerfile`, `docs/livraison.md`, `scripts/conformite.py` |
| **C20** | 🟢 | Journaux JSON Lines pseudonymisés, `X-Request-ID` traversant app → API, seuils, alertes, tableau de bord local `/exploitation`. | `docs/monitoring-app.md`, `monitoring/` |
| **C21** | 🟢 | **Cinq incidents réels** : reproduction, diagnostic, correctif minimal, non-régression vérifiée **dans les deux sens**, REX. | `docs/incident.md` |

**À montrer** : la bascule de profil (même calcul), la porte de conformité qui refuse,
un incident de bout en bout.

---

## Les cinq incidents (C21)

| Identifiant | Nature | Ce qu'il enseigne |
|---|---|---|
| `CI-2026-08-24` | Ordre d'initialisation PostgreSQL, puis packaging incomplet | Un lancement local masque une erreur de packaging |
| `APP-2026-08-25` | Bascule de profil renvoyant `405` en pleine démonstration | Un lien relatif suppose le verbe HTTP de la page courante |
| `CI-2026-08-25` | Tests verts en local, rouges en CI (`503`) | Le poste fournissait silencieusement un service démarré |
| `SEC-2026-08-25` | Deux dépendances vulnérables détectées par la porte | La chaîne d'approvisionnement doit être auditée, pas supposée |
| `SEC-2026-08-25-bis` | La porte déclarait conforme une chaîne cassée | **Un artefact valide ne prouve que le passé** |

**Motif récurrent, quatre fois sur cinq** : la documentation affirmait ce que le code ne faisait pas
(registre RGPD, versionnement DVC, tracking MLflow). Chaque correction a rendu l'affirmation vraie
**et** l'a fait vérifier par un test ou un critère.

## Limites assumées devant le jury

- **C6 et C16 partiels** : le référentiel attend un travail collectif animé. Le candidat est seul.
  Aucune équipe n'est simulée.
- **Métriques de règles circulaires** : les règles de cohérence et les anomalies du jeu de
  démonstration relèvent des mêmes familles. Seul l'**AUC 0,9095 de l'auto-encodeur** est informatif,
  car il n'a vu ni les règles ni les étiquettes.
- **Base DPE non représentative** du parc français : l'ADEME demande une lecture prudente.
  Aucune généralisation nationale.
- **Rapprochement par parcelle cadastrale** : ambigu en copropriété. Le système le signale
  (`nb_dpe_candidats`) sans le résoudre.
- **Aucune prédiction de prix ni tarification.** C'est un choix de périmètre, pas une lacune.

## Reproduction complète

```bash
source scripts/spark-env.sh          # JDK 17 + SPARK_LOCAL_IP, requis hors ligne
docker compose up -d                 # PostgreSQL 17
python scripts/make_sample_fixture.py
python -m concorde.collect && python -m concorde.clean
python -m concorde.model.entrainement
pytest -m "not local_service"        # 52 tests
python scripts/conformite.py         # porte : 12 critères, code de sortie 0
```
