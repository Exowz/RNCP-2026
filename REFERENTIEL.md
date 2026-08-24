# RNCP — Développeur en intelligence artificielle (Simplon 2023, via ECE)

Source : `séance 1/[Dev IA 2023] Referentiel Activites Competences et evaluation.pdf` (25 p.)
et `séance 1/Coaching_ECE_Simplon_Ref (1).pdf` (33 p., K. Kadri, ECE, 2026).
Textes bruts conservés dans `referentiel_raw.txt` et `coaching_raw.txt`.

## Le principe, en une phrase

> Le projet doit être pensé comme une chaîne complète :
> **données → modèle/service IA → API → application → tests → monitoring → soutenance.**

Et la règle d'or du coaching :

> Une slide ne doit pas raconter ce qui a été fait, elle doit **prouver** qu'une compétence est réalisée.
> Aucune compétence ne doit rester au statut « on l'a fait » : elle doit être reliée à une preuve
> localisable (chemin Git, capture, commande de reproduction, résultat de test).

## Les 5 évaluations

Chacune donne lieu à **un rapport professionnel individuel** et **une soutenance orale individuelle**.
C'est de là que viennent les « cinq soutenances ».

| Éval. | Type | Compétences | Contexte imposé | Livrable |
|---|---|---|---|---|
| **E1** | Mise en situation | C1–C5 | Réalisation d'un service numérique réel ou fictif basé sur l'usage de données | Rapport professionnel individuel |
| **E2** | Cas pratique | C6–C8 | À partir de l'expression d'un besoin réel ou fictif | Rapport professionnel individuel |
| **E3** | Mise en situation | C9–C13 | Mise en service d'un modèle **fourni** et intégration dans une application existante | Rapport + soutenance **avec démonstration** |
| **E4** | Mise en situation | C14–C19 | Développement d'une application intégrant un service d'IA | Rapport + soutenance **avec démonstration** |
| **E5** | Cas pratique | C20–C21 | Application existante présentant **au moins une erreur technique** | Documentation du monitorage + de la résolution d'incident |

Note : « réel ou fictif » est écrit noir sur blanc pour E1, E3, E4 et E5. Le contexte peut être inventé ;
les preuves techniques, non.

## Les 3 blocs et les 21 compétences

### Bloc 1 — Collecter, stocker et mettre à disposition les données (C1–C5)

| Comp. | Énoncé (résumé fidèle) | Preuve minimale attendue |
|---|---|---|
| **C1** | Automatiser l'extraction depuis **un service web, une page web (scraping), un fichier de données, une base de données ET un système big data** | Scripts, logs, fichiers bruts. Point d'entrée clair, gestion d'erreurs, sauvegarde, versionné Git |
| **C2** | Développer des **requêtes SQL** d'extraction depuis un SGBD **et un système big data** | Requêtes documentées (jointures, filtres, optimisations) + résultats |
| **C3** | Règles d'**agrégation** multi-sources : suppression des entrées corrompues, homogénéisation des formats | Dataset final versionné, règles écrites, tableau avant/après, tests qualité |
| **C4** | Créer une base de données **dans le respect du RGPD** : MCD, MPD, import programmatique | MCD/MPD, choix SGBD, script d'import, registre RGPD, procédure d'installation |
| **C5** | Développer une **API REST** mettant le jeu de données à disposition | Routes, authentification, documentation OpenAPI, exemples de requêtes |

### Bloc 2 — Intégrer modèles et services IA, API, MLOps (C6–C13)

| Comp. | Énoncé (résumé fidèle) | Preuve minimale attendue |
|---|---|---|
| **C6** | Organiser et réaliser une **veille technique et réglementaire**, en animant le travail collectif | Thématique claire, sources qualifiées, planning, outil d'agrégation, outil de partage |
| **C7** | Identifier des **services d'IA préexistants** : benchmark, analyse, recommandation | Tableau comparatif avec services **retenus et écartés**, décision argumentée |
| **C8** | **Paramétrer** un service d'IA selon sa documentation et les spécifications | Installation, accès/authentification, dépendances, monitoring disponible |
| **C9** | Développer une **API REST exposant un modèle** d'IA | Endpoint `/predict`, auth, validation des entrées, tests, OpenAPI |
| **C10** | **Intégrer l'API** du modèle dans une application, normes d'accessibilité | L'app appelle réellement l'API, le résultat modifie l'UX, erreurs gérées |
| **C11** | **Monitorer le modèle** : métriques courantes et spécifiques, alertes, restitution | Performance, dérive des données, latence, erreurs, santé système + dashboard |
| **C12** | **Tests automatisés** du modèle : validation des jeux de données, préparation, entraînement, évaluation | Tests sur format, preprocessing, prédiction, validation, endpoints + couverture |
| **C13** | **Chaîne de livraison continue** du modèle, approche MLOps | Pipeline : tests → entraînement/évaluation → rapport → packaging → livraison |

### Bloc 3 — Application IA complète, CI/CD, MCO (C14–C21)

| Comp. | Énoncé (résumé fidèle) | Preuve minimale attendue |
|---|---|---|
| **C14** | **Analyser le besoin** d'application : spécifications fonctionnelles, modélisation, utilisabilité et accessibilité | Personas, user stories, critères d'acceptation, exigences d'accessibilité (WCAG/RGAA) |
| **C15** | **Concevoir le cadre technique** : architecture technique et applicative, outils et méthodes | Schémas, flux de données, dépendances, services externes, POC |
| **C16** | **Coordonner** la réalisation en conduite agile et contexte MLOps | Kanban, rôles, rituels, backlog, exemple de décision après blocage |
| **C17** | **Développer** composants et interfaces : accessibilité, sécurité, gestion des données | UI conforme aux maquettes, droits et accès, sécurité OWASP, tests métier, docs |
| **C18** | **Automatiser les tests** au versionnement via intégration continue | Workflow GitHub Actions / GitLab CI, exécution des tests, statut compris |
| **C19** | **Processus de livraison continue** de l'application | Build ou image Docker, packaging, livraison en pré-production, procédure documentée |
| **C20** | **Surveiller l'application** : monitorage et journalisation, RGPD, feedback loop MLOps | Logs, métriques, seuils, alertes, dashboard |
| **C21** | **Résoudre les incidents** techniques et documenter les solutions | Incident décrit, diagnostic, hypothèse, correction, test de non-régression, REX |

## Structure imposée du rapport professionnel

1. Contexte, acteurs, objectifs, contraintes
2. Spécifications fonctionnelles et techniques
3. Réalisation data, IA, API, application
4. Tests, CI/CD, monitoring, sécurité, accessibilité
5. Bilan, limites, décisions et perspectives

Chaque section doit contenir **une décision technique, une preuve, une capture, un lien Git, une
commande de reproduction ou un résultat de test**.

## Structure recommandée de la soutenance

1. Contexte, besoin, acteurs, contraintes
2. Architecture globale et flux de données
3. Bloc 1 : preuves data C1–C5
4. Bloc 2 : preuves IA/API/MLOps C6–C13
5. Bloc 3 : preuves app/CI/CD/MCO C14–C21
6. Démonstration live courte
7. Bilan, limites, améliorations

Chaque slide porte un bandeau discret : **Compétences prouvées : Cx, Cy**.

Test de validation d'une slide : si on enlève le titre, le jury doit encore comprendre quelle
compétence est prouvée par la capture, le schéma ou le résultat affiché.

## Structure imposée du dépôt Git

```
project-ai-ece/
  README.md
  docs/               # specs, architecture, RGPD, benchmark
  data/               # raw, processed, samples
  notebooks/          # exploration uniquement
  src/                # collecte, nettoyage, features, model
  api/                # API data et API model
  app/                # front ou application
  tests/              # tests data, API, modèle, app
  monitoring/         # logs, métriques, dashboards
  .github/workflows/  # CI/CD
  reports/            # rapport, captures, annexes
```

Piège explicite : **le notebook unique** qui contient tout.

## Les 7 pièges majeurs (liste du coaching)

1. Tout miser sur le modèle IA et oublier data / API / tests / monitoring
2. Faire une soutenance narrative sans preuves
3. Ne pas versionner les scripts et configurations
4. Avoir une API sans authentification ni OpenAPI
5. Oublier accessibilité, RGPD, sécurité OWASP
6. Ajouter CI/CD et monitoring la dernière semaine
7. Ne pas préparer d'incident technique documenté

## Checklist avant soutenance

**Technique** : dépôt Git accessible · README reproductible · tests exécutables · API documentée ·
démo préparée **hors internet**.

**Jury** : matrice compétences/preuves · captures lisibles · décisions justifiées · limites assumées ·
chaque étudiant connaît sa partie.

## Matrice de preuves — à remplir

| Comp. | Preuve technique | Où dans Git / rapport | Slide |
|---|---|---|---|
| C1 | | | |
| C2 | | | |
| C3 | | | |
| C4 | | | |
| C5 | | | |
| C6 | | | |
| C7 | | | |
| C8 | | | |
| C9 | | | |
| C10 | | | |
| C11 | | | |
| C12 | | | |
| C13 | | | |
| C14 | | | |
| C15 | | | |
| C16 | | | |
| C17 | | | |
| C18 | | | |
| C19 | | | |
| C20 | | | |
| C21 | | | |
