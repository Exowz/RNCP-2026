# Spécification — front web Next.js (`app/web`)

Document de cadrage. Destiné à l'agent qui implémente le front, et défendable
devant le jury comme spécification technique (C14, C15).

---

## 1. Objectif

Ajouter un **second client** à l'API Concorde, écrit en Next.js.

L'intérêt n'est pas cosmétique. Une API consommée par deux clients indépendants
cesse d'être un utilitaire de gabarit et devient un **contrat** : c'est un
argument direct pour C9, et cela prouve que le découplage annoncé est réel.

Objectif secondaire, aussi important : **le produit doit devenir compréhensible
sans explication orale**. L'application Jinja actuelle affiche des identifiants
de base de données là où l'utilisateur attend des objets du monde. Le front
Next.js est l'occasion de corriger cela (section 6).

## 2. Ce qu'il ne faut PAS toucher

Six compétences sont actuellement au vert et prouvées. Toute régression sur ces
fichiers coûte plus qu'elle ne rapporte :

| Chemin | Ce qu'il prouve |
|---|---|
| `app/main.py`, `app/templates/`, `app/static/` | C10, C14, C17, C20 — appel HTTP réel, accessibilité testée, page `/exploitation`, corrélation `X-Request-ID` |
| `api/model/` | C9 — `/predict`, auth, OpenAPI, validation stricte |
| `src/concorde/**` | C1–C3, C11–C13 — collecte, nettoyage, modèle, monitoring |
| `.github/workflows/verify.yml` | C18 — CI verte, à ne pas casser |
| `tests/**` | C12 — 23 tests verts |

**L'application Jinja reste le livrable évalué.** Le front Next.js est un ajout.
S'il n'est pas prêt le jour de la soutenance, on présente l'app Jinja et rien
n'est perdu.

## 3. Architecture cible

```
navigateur
    │  HTTP (aucune clé d'API côté client)
    ▼
Next.js  app/web  :3000
    │  Route Handlers côté serveur — portent la clé d'API
    ├──────────────► API data   :8001   (liste des rapprochements)
    └──────────────► API modèle :8002   (POST /predict, /regles, /modele/fiche)
```

Ports : `3000` Next.js · `8000` app Jinja · `8001` API data · `8002` API modèle.

## 4. Contraintes non négociables

### 4.1 La clé d'API ne doit JAMAIS atteindre le navigateur

C'est le piège le plus grave, et il touche **C17**.

L'API exige l'en-tête `X-API-Key`. Si le composant client appelle
`http://127.0.0.1:8002/predict` directement, la clé part dans le bundle
JavaScript et se lit dans l'onglet Réseau. Ce serait une fuite de secret dans un
projet dont la sécurité est notée.

**Obligatoire** : tout appel à l'API passe par un *Route Handler* Next.js
(`app/api/.../route.ts`) ou un Server Component. La clé est lue depuis une
variable d'environnement **sans** préfixe `NEXT_PUBLIC_`.

Bénéfice annexe : aucun CORS à configurer sur l'API Python, puisque le
navigateur ne lui parle jamais.

Variable attendue : `CONCORDE_API_KEY=dev-analyst-key` dans `app/web/.env.local`,
et `.env.local` **doit** rester dans `.gitignore`.

### 4.2 La démonstration doit fonctionner hors ligne

Contrainte d'examen, sans exception.

- `bun install` **doit être fait maintenant**, tant qu'il y a du réseau. Le
  lockfile `bun.lock` est versionné.
- **Aucune police distante.** Pas de `next/font/google` (télécharge au build).
  Utiliser une pile de polices système, ou `next/font/local` avec le fichier
  dans `public/`.
- **Aucune image, aucun script, aucune feuille de style distante.** Pas de CDN.
- La démo tourne sur un **build de production** : `bun run build` puis
  `bun run start`. Le build doit être fait **avant** la soutenance, pas devant
  le jury.
- Critère de recette : couper le Wi-Fi, lancer `bun run start`, le parcours
  complet doit fonctionner.

### 4.3 Parité d'accessibilité (C14, C17)

Le front Jinja actuel est conforme et testé. Le front Next.js ne doit pas
régresser :

- `<html lang="fr">`
- lien d'évitement, premier élément focusable, visible au focus
- repères sémantiques : `header`, `nav` nommée, `main`, `footer`
- focus visible partout, jamais de `outline: none` sans remplacement
- contrastes ≥ 4,5:1 — la palette de `app/static/concorde.css` est déjà
  calibrée et documentée, la réutiliser
- le sens n'est jamais porté par la seule couleur : toujours un libellé
- résultat annoncé par `aria-live="polite"`
- erreurs avec `role="alert"`
- `prefers-reduced-motion` respecté
- aucun défilement horizontal sous 320 px

### 4.4 Ne pas dégrader la CI

Si un job Node est ajouté à `verify.yml`, il doit être **séparé** du job Python
existant, pour qu'un échec front ne fasse pas passer au rouge la preuve C18 déjà
acquise.

## 5. Travail préalable côté API (C5)

L'API data n'expose aujourd'hui que `/sante` et `/communes`. C'est insuffisant
pour alimenter un front, et c'est une faiblesse de C5.

**À ajouter dans `api/data/` :**

- `GET /rapprochements` — liste paginée, filtrable par `code_commune`,
  `niveau_confiance`, `avec_dpe`. Authentifiée (`reader`), documentée OpenAPI,
  avec un schéma Pydantic de sortie.
- `GET /rapprochements/{id_mutation}` — le détail d'un rapprochement, dans un
  format directement soumissible à `POST /predict` de l'API modèle.
- `GET /rapprochements/demonstration` — les cinq cas pédagogiques. Réutiliser la
  logique existante de `app/exemples.py` (filtres déterministes sur la table
  réelle) plutôt que de la réécrire ; l'extraire dans `src/concorde/` si besoin
  de la partager.

Chaque route : un test dans `tests/api/test_api_data.py`.

**Important** : ces réponses doivent porter les **noms** et pas seulement les
codes — `nom_commune`, `etiquette_dpe`, `adresse_ban` sont présents dans
`data/processed/rapprochements.parquet` et ne sont pas exposés aujourd'hui.

## 6. Le cœur du travail : rendre le produit compréhensible

C'est la raison d'être de ce chantier. Un utilisateur qui arrive sur
l'application ne comprend pas ce qu'il regarde. Cinq défauts à corriger.

### 6.1 Parler du monde, pas de la base de données

| Aujourd'hui | Attendu |
|---|---|
| `commune 24016` | `Annesse-et-Beaulieu (24)` |
| `Mutation 2023-100011` | `Appartement de 79 m², vendu en mars 2024` |
| étiquette DPE jamais affichée | Étiquette `E` visible, avec l'échelle A→G |
| `parcelle 24016000Z0125` | à reléguer dans le détail technique |

### 6.2 Définir le vocabulaire

« DVF+ », « DPE », « rapprochement », « mutation », « parcelle » ne sont jamais
définis. Prévoir une définition courte au premier emploi — infobulle accessible
ou élément `<dfn>`, jamais un survol seul (inaccessible au clavier).

Formulations de référence :

- **DVF+** — le registre public des ventes immobilières déjà conclues, issu des
  actes notariés. *Il ne contient pas les biens en vente.*
- **DPE** — le diagnostic de performance énergétique, l'étiquette A à G.
- **Rapprochement** — l'association d'une vente et d'un diagnostic dont on
  suppose qu'ils décrivent le même logement. *C'est cette supposition que
  Concorde vérifie.*

### 6.3 Donner une échelle aux nombres

« Cohérence 60 % » ne veut rien dire seul. Chaque score doit porter sa lecture :
ce que vaut 100 %, ce qui est bon, ce qui est préoccupant. Une barre, une
échelle, ou une phrase — mais jamais un pourcentage nu.

### 6.4 Énoncer le « pourquoi » dès la première page

L'idée centrale n'apparaît nulle part à l'écran. Elle doit être la première
chose lue :

> Deux bases publiques décrivent le même logement sans partager d'identifiant
> fiable. Quand on les croise, le rapprochement peut être faux — et rien ne vous
> le signale. Concorde vous dit quand vous pouvez y croire.

Et son pendant, tout aussi visible :

> Concorde n'estime aucun prix et ne produit aucune tarification.

### 6.5 Rendre la chaîne visible

Rien ne laisse deviner qu'il y a cinq sources, un nettoyage, un modèle et une CI
derrière ces écrans. Une page « Comment ça marche » avec le schéma de la chaîne
et **les volumes réels** (1 735 lignes brutes → 922 rapprochements → 716
appariés → 206 sans DPE) sert à la fois l'utilisateur et la preuve C15.

## 7. Écrans attendus

1. **Accueil** — le « pourquoi » (6.4), puis les cas de démonstration décrits en
   langage humain (6.1).
2. **Résultat** — les trois axes avec leur échelle (6.3), les motifs, les
   réserves, l'exposition aux aléas. Deux profils : particulier (phrases) et
   analyste (identifiants de règles, décomposition de l'écart, version du
   modèle). **Le profil change la restitution, jamais le calcul.**
3. **Comment ça marche** — la chaîne et ses volumes (6.5).
4. **Transparence** — les règles avec leur seuil et leur justification, servies
   par `GET /regles` de l'API. Ne pas les recopier en dur : elles doivent venir
   du code exécuté.

Note : la bascule de profil doit conserver le cas évalué. Un incident déjà
documenté (`APP-2026-08-25`) portait exactement sur ce point côté Jinja.

## 8. Critères d'acceptation

- [ ] `bun run build` puis `bun run start` : parcours complet **Wi-Fi coupé**.
- [ ] Onglet Réseau du navigateur : **aucune** requête vers un domaine externe,
      **aucune** occurrence de la clé d'API.
- [ ] `grep -r "NEXT_PUBLIC.*KEY" app/web` ne renvoie rien.
- [ ] Navigation complète au clavier seul, focus visible en permanence.
- [ ] Les 23 tests Python passent toujours : `pytest -m "not local_service"`.
- [ ] L'app Jinja sur `:8000` fonctionne toujours à l'identique.
- [ ] Un utilisateur qui n'a jamais vu le projet comprend, sans commentaire
      oral, ce que fait Concorde et ce qu'il refuse de faire.

Le dernier critère est le seul qui compte vraiment. C'est celui qui a échoué
jusqu'ici.

## 9. Rappel des commandes

```bash
# Services Python (préalable)
source scripts/spark-env.sh
docker compose up -d
.venv/bin/uvicorn api.data.main:app  --host 127.0.0.1 --port 8001 &
.venv/bin/uvicorn api.model.main:app --host 127.0.0.1 --port 8002 &

# Front
cd app/web
bun install          # PENDANT QU'IL Y A DU RÉSEAU
bun run build
bun run start        # http://127.0.0.1:3000
```
