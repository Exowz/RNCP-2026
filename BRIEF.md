# Brief de démarrage — Projet RNCP 2026

Document de passation. À lire en premier dans la nouvelle session Claude Code.
Le référentiel complet est dans `REFERENTIEL.md` (même dossier), les textes bruts des PDF
sources dans `referentiel_raw.txt` et `coaching_raw.txt`.

## Situation

- **Certification** : RNCP « Développeur en intelligence artificielle » (référentiel Simplon 2023, via ECE Paris).
- **Examen : 27 août 2026.** Aujourd'hui le 24. **Trois jours.**
- **Candidat seul.** Aucun coaching reçu (il était réservé aux alternants).
- **Point de départ : zéro.** Aucun code, aucun rapport, aucun dépôt.
- Assisté par deux IA (Claude Code + Codex). La vitesse d'écriture n'est pas le facteur limitant ;
  la **défendabilité à l'oral** l'est.

## La décision, déjà prise

**Un seul projet, un seul dépôt, deux livrables.**

1. **Le socle technique** est le *projet de substitution n°21* du cours de ML/DL (déposant : Foued Derraz) :
   « Secure MLOps : validation de la sécurité des modèles IA ». Une chaîne CI/CD qui évalue
   automatiquement qualité, robustesse et sécurité d'un modèle avant mise en production.
   Stack imposée : Python, PyTorch, MLflow, DVC, Evidently, Docker, GitHub Actions.
   Livrable : usine logicielle IA avec tableau de conformité avant déploiement.
   *Le candidat le fait seul, c'est validé. Aucune déclaration croisée à faire entre les deux
   évaluations — il choisit librement son projet RNCP.*

2. **Le domaine** est une version **resserrée** de ClimateCollateral : un modèle
   **d'anomalie, de cohérence et de confiance** sur le croisement transactions immobilières ×
   DPE × exposition aux aléas.
   **Pas de prédiction de prix. Pas de tarification.** La question posée est : ce rapprochement
   est-il fiable, cette donnée est-elle cohérente, quel est mon niveau de confiance.

3. **Ce que le RNCP exige en plus du n°21** : une couche de **données** en amont (bloc 1) et une
   **application** en aval (bloc 3), plus la veille et le service IA tiers (C6–C8).

Deux publics pour l'application, à la manière de RiskLens :
- un particulier — « ce que les données permettent réellement de savoir sur ce bien, et ce qu'elles ne permettent pas d'inférer » ;
- un analyste crédit / underwriting — comparables, exposition, qualité du rapprochement, variables manquantes.

**Ligne de défense unique, à tenir partout :** « je ne remplace pas la décision ; je réduis l'écart
entre des données complexes et une décision informée, en rendant visibles les sources, les
hypothèses et les inconnues. »

## Ce que le n°21 couvre réellement (analyse Codex, à ne pas surestimer)

| Statut | Compétences |
|---|---|
| **Couvert** | C12 (tests automatisés), C13 (chaîne validation → entraînement/éval → packaging → livraison) |
| **Partiel, sous condition** | C11 (si Evidently mesure vraiment performance, dérive, latence, alertes) · C18/C19 (si GitHub Actions **s'exécute** réellement) · C9 (API annoncée, mais auth/validation/OpenAPI/tests à prouver) · C17 (sécurité du modèle ≠ sécurité applicative) · C20 (Evidently surveille le modèle, pas l'app ni ses logs) |
| **Entièrement à construire** | **C1–C5**, **C6–C8**, C10, **C14–C16**, une part substantielle de C17 et C20, et **C21 en entier** |

Le piège à éviter : croire que Secure MLOps couvre automatiquement le RNCP. Il ne le fait pas.

## Sources de données (vérifiées, volumes réels)

| Source | Contenu | Rôle dans C1/C2 |
|---|---|---|
| **DVF+** (DGALN / Cerema, data.gouv.fr) | Transactions immobilières géolocalisées, une ligne par mutation | **Fichier** |
| **DPE** — Observatoire DPE-Audit (ADEME) | Tous les DPE depuis le 01/07/2021 ; jeu historique > 10 M de DPE | **Système big data** (parquet + Spark SQL) |
| **Base Adresse Nationale** (DINUM/IGN) | 26,11 M d'adresses ; fichiers, flux et API, MAJ quotidienne | **Service web** (API) |
| **Géorisques** (BRGM / ministère) | API + jeux téléchargeables : inondation, retrait-gonflement des argiles, cavités | **Service web** (API) |
| **PostgreSQL** local | Base du projet, modélisée MCD/MPD | **SGBD** |
| Scraping ciblé | Une fiche ou page publique précise, usage limité et documenté | **Page web** |

⚠️ La base DPE **n'est pas représentative** du parc français : l'ADEME demande explicitement une
interprétation prudente. Toute inférence doit afficher son niveau de confiance. Ce n'est pas une
faiblesse à masquer, c'est le cœur du produit.

## Règle de décision sur C7/C8 (la plus mal comprise)

C7 exige un **benchmark de services IA préexistants** — retenus **et écartés**, raisons
d'exclusion, contraintes techniques, démarche éco-responsable. C8 exige un service **installé,
accessible, configuré, monitoré et documenté**.

- Un modèle scikit-learn importé dans une API **ne suffit pas**.
- Un **service local préexistant** (type Ollama servant un modèle préchargé, ou un service
  d'extraction), exposé en HTTP, avec droits d'accès, paramètres, métriques et procédures de test :
  **défendable**, et compatible avec la démo hors ligne.
- Doctrine : **données structurées d'abord**, service IA local **seulement sur le résidu réellement
  non structuré**. « Mettre un LLM pour avoir un LLM » se défait en deux questions.

## Contraintes non négociables

- **Démo strictement hors ligne.** Pas seulement « Internet coupé » : ni téléchargement de modèle,
  ni appel d'API, ni CDN, ni base externe, ni image Docker absente. Poids, données, dépendances et
  scénarios doivent être présents **avant**.
- **Preuve avant code.** Chaque demi-journée produit : du code qui tourne + une capture ou un log
  exploitable + un paragraphe rangé dans la bonne section de rapport. Aucune compétence au statut
  « on l'a fait ».
- **Tags Git sur les états stables et démontrables** (`v1-substitution`, `v1-rncp`). Raison purement
  pratique : pouvoir démontrer depuis un état sain si le dépôt est cassé la veille. Ce n'est **pas**
  une exigence de traçabilité de contribution — le candidat est seul auteur.
- **Tranche verticale d'abord** : une petite version bout-en-bout (données → modèle → API → app →
  test → log → démo offline) vaut mieux que des briques ambitieuses isolées.

## Ce qu'on peut bâcler / ce qu'on ne peut pas

**Bâclable** : design visuel, fonctions secondaires, gestion de comptes complexe, temps réel, cloud,
deep learning sophistiqué, ambition prédictive.

**Non bâclable** : C1/C2 · authentification et OpenAPI (C5/C9) · accessibilité et sécurité (C14/C17) ·
tests (C12/C18) · **exécution réelle** de la CI/CD (C13/C19) · monitoring (C11/C20) · incident (C21) ·
reproductibilité hors ligne.

## Limites à assumer devant le jury, pas à masquer

- **C6 et C16** exigent un travail collectif (animation, rôles, rituels). Le candidat est seul.
  Montrer un Kanban personnel, un journal de décisions daté, une rétrospective individuelle — et
  **dire que la couverture est partielle**. Ne jamais simuler une équipe.
- **E3** suppose un « modèle fourni » et une « application existante ». Le dépôt est neuf.
  Mise en scène honnête : un artefact de modèle **gelé et versionné**, avec sa fiche, présenté comme
  la livraison d'une équipe Data Science à l'équipe applicative. Le référentiel autorise
  explicitement un contexte « réel ou fictif ».
- **Rapprochement adresse × mutation × DPE** parfois ambigu ou incomplet : c'est le sujet, pas un bug.

## Structure du dépôt (imposée par le coaching)

```
projet/
  README.md
  docs/               # specs, architecture, RGPD, benchmark, veille
  data/               # raw, processed, samples
  notebooks/          # exploration uniquement
  src/                # collecte, nettoyage, features, model
  api/                # API data (C5) et API modèle (C9)
  app/                # application (C10, C14-C17)
  tests/              # tests data, API, modèle, app
  monitoring/         # logs, métriques, dashboards
  .github/workflows/  # CI/CD
  reports/
    rncp/             # les 5 rapports E1-E5, matrice de preuves, slides RNCP
    substitution/     # rapport n°21, doc du tableau de conformité, slides Derraz
```

Piège explicite du coaching : **le notebook unique** qui contient tout.

### Substitution et RNCP dans un seul dépôt

**Le code n'est pas dupliqué et n'a pas à l'être** : c'est un seul système. Ce qui se sépare, ce sont
les **livrables**, parce qu'ils s'adressent à deux lecteurs qui lisent le même dépôt sous deux angles.

- **Substitution (M. Derraz)** : ne regarde que l'**usine** — CI/CD, tests, MLflow, DVC, Evidently,
  Docker, tableau de conformité avant déploiement. Le domaine immobilier n'est pour lui que le cas
  d'usage qui alimente l'usine. Le sujet n°21 autorise explicitement les « datasets tabulaires » et
  les « jeux maison », donc le jeu de données construit ici entre dans son cadre sans justification.
- **RNCP** : regarde la **chaîne complète**, dont l'usine n'est qu'un tiers (bloc 3). Il faut en plus
  la couche données en amont (C1-C5) et l'application en aval (C14-C17).

Rien à déclarer de part et d'autre : le candidat choisit librement son sujet de RNCP, et le projet de
substitution n'a pas à mentionner le RNCP.

## Matrice de preuves — état de soutenance

| Comp. | Preuve visée | Emplacement | Slide | Fait |
|---|---|---|---|---|
| C1 | Script de collecte 5 sources + logs + arborescence `data/raw/` | `src/collect/` | | ✅ |
| C2 | Requêtes SQL PostgreSQL **et** Spark SQL, documentées (jointures, filtres, optimisations) | `docs/queries.md` | | ✅ |
| C3 | Script d'agrégation, tableau avant/après, règles de nettoyage, dataset versionné | `src/clean/` | | ✅ |
| C4 | MCD + MPD, script d'import, registre RGPD, procédure d'installation | `docs/data-model.md` | | ✅ |
| C5 | API data REST : routes, auth, OpenAPI, exemples | `api/data/` | | ✅ |
| C6 | Journal de veille daté, sources qualifiées, synthèse, preuve de partage | `docs/veille.md` | | 🟡 limite assumée |
| C7 | Benchmark services IA : retenus **et écartés**, critères dont éco-responsabilité | `docs/benchmark.md` | | ✅ |
| C8 | Installation + configuration + accès + monitorage du service retenu | `docs/service-ia.md` | | ✅ |
| C9 | `/predict` : auth, validation des entrées, OpenAPI, tests | `api/model/` | | ✅ |
| C10 | L'app appelle réellement l'API ; erreurs gérées ; accessibilité | `app/` | | ✅ |
| C11 | Evidently : performance, dérive, latence, erreurs + alertes | `monitoring/model/` | | ✅ |
| C12 | Tests format, preprocessing, prédiction, seuil, endpoints + couverture | `tests/` | | ✅ |
| C13 | Pipeline exécuté : tests → entraînement/éval → rapport → packaging → livraison | `.github/workflows/` | | ✅ |
| C14 | Personas, user stories, critères d'acceptation, exigences WCAG/RGAA | `docs/specs-fonctionnelles.md` | | ✅ |
| C15 | Architecture, flux de données, dépendances, services externes, POC | `docs/architecture.md` | | ✅ |
| C16 | Kanban, backlog, journal de décisions daté, rétrospective — **limite assumée** | `docs/pilotage.md` | | 🟡 limite assumée |
| C17 | Droits et accès, OWASP, validation entrées, journalisation, accessibilité | `app/`, `docs/securite.md` | | ✅ |
| C18 | Capture d'**exécution réussie** du workflow CI | `.github/workflows/` | | ✅ |
| C19 | Build/image Docker, packaging, livraison préproduction locale, procédure | `docs/livraison.md` | | ✅ |
| C20 | Logs applicatifs, métriques, seuils, alertes, dashboard | `monitoring/app/` | | ✅ |
| C21 | Incident **réel** : ticket, log, reproduction, diagnostic, commit correctif, test avant/après | `docs/incident.md` | | ✅ |

## Structure des 5 rapports (identique pour chacun)

1. Contexte, acteurs, objectifs, contraintes
2. Spécifications fonctionnelles et techniques
3. Réalisation data, IA, API, application
4. Tests, CI/CD, monitoring, sécurité, accessibilité
5. Bilan, limites, décisions et perspectives

Chaque section contient une **décision technique**, une **preuve**, une **capture**, un **lien Git**,
une **commande de reproduction** ou un **résultat de test**.

Répartition : E1 → C1–C5 · E2 → C6–C8 · E3 → C9–C13 (avec démo) · E4 → C14–C19 (avec démo) ·
E5 → C20–C21 (documentation du monitorage et de l'incident).

## Soutenance

1. Contexte, besoin, acteurs, contraintes — 2. Architecture globale et flux — 3. Bloc 1 (C1–C5) —
4. Bloc 2 (C6–C13) — 5. Bloc 3 (C14–C21) — 6. Démonstration live courte — 7. Bilan et limites.

Bandeau discret sur chaque slide : **Compétences prouvées : Cx, Cy**.
Test de validation : si on retire le titre, le jury doit encore comprendre quelle compétence est
prouvée par la capture ou le résultat affiché.

## Plan des trois jours

- **J1 (24)** — Squelette du dépôt à la structure imposée. Bloc 1 en entier : les cinq sources, Spark
  sur les DPE, MCD/MPD, registre RGPD, API data. **Tranche verticale minimale bout-en-bout dès ce soir.**
- **J2 (25)** — Veille + benchmark + service IA local (C6–C8). API modèle, tests, Evidently, chaîne
  MLOps (C9–C13). C'est le cœur du n°21.
- **J3 (26)** — Application et accessibilité (C10, C14–C17), CI/CD exécutée (C18–C19), monitoring
  applicatif (C20), **incident provoqué, corrigé et testé** (C21). Puis les cinq rapports et les slides,
  à partir des preuves déjà accumulées.
- **27** — Soutenances.

Sécuriser en priorité ce qui est irrattrapable tard : les sources, Spark, le modèle disponible hors
ligne, le cache local, le dépôt distant.

## Dernier avertissement

Une couverture exhaustive des 21 compétences en trois jours reste **très risquée**, même avec deux IA.
Mieux vaut un système **étroit, complet, traçable et démontrable hors ligne** qu'un système large et
troué. Le danger à l'oral n'est pas la vitesse de production du code : c'est l'incapacité à expliquer
un rôle, un compromis, un seuil. Chaque ligne structurante doit être comprise indépendamment des IA.
