# Atlas cadastral Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Recomposer le second client Next.js en atlas cadastral de preuve qui explique la convergence incertaine DVF+/DPE, sans rompre les garanties RNCP.

**Architecture:** Les Server Components, leurs appels serveur et les contrats de l'API restent inchangés. La composition JSX et le système CSS deviennent une carte de lecture locale : des repères, des trajectoires et des annotations remplacent le cadrage de dossier. Aucun nouvel actif réseau ni composant client n'est introduit.

**Tech Stack:** Next.js 16, React 19, TypeScript, Tailwind 4 importé, CSS local, Bun.

**Spec:** `docs/superpowers/specs/2026-08-25-atlas-cadastral-design.md`

## Global Constraints

- Ne modifier que `app/web/**`, `DESIGN.md` et `docs/journal-decisions.md`.
- Utiliser Bun ; ne pas introduire npm, pnpm ou yarn.
- Ne charger ni police, image, script ou feuille de style distante ; ne pas importer `next/font/google`.
- Ne jamais exposer `CONCORDE_API_KEY` au navigateur ni créer de variable `NEXT_PUBLIC_*KEY`.
- Conserver les repères sémantiques, le lien d'évitement, le focus visible, `aria-live`, `role=alert`, les contrastes et `prefers-reduced-motion`.
- Le rendu doit rester utilisable à 20 rem et ne jamais créer de défilement horizontal.
- L'application Jinja, les API Python, `src/concorde/**`, `tests/**` et la CI Python ne changent pas.

---

### Task 1: Établir les références visuelles et le système de mouvement

**Files:**
- Modify: `DESIGN.md`
- Modify: `app/web/app/globals.css`

**Interfaces:**
- Consumes: la spécification Atlas cadastral et les composants existants.
- Produces: les tokens CSS `--atlas-*`, les motifs décoratifs locaux et les classes de mouvement réutilisables par les quatre écrans.

- [ ] **Step 1: Produire et comparer des références locales**

Utiliser les skills `imagegen-frontend-web`, `imagegen-frontend-mobile`, `brandkit` et `image-to-code` comme atelier de référence, sans intégrer de bitmap ni URL externe au produit. Retenir les constantes compatibles avec la contrainte hors ligne : grille topographique, repères de coordonnées, traits de convergence, hiérarchie sérif/sans/mono.

- [ ] **Step 2: Auditer les directions contradictoires**

Faire passer `minimalist-ui`, `industrial-brutalist-ui`, `design-taste-frontend-v1` et `gpt-taste` comme contre-lectures. Garder la clarté minimaliste et la rigueur de grille ; écarter le brutalism agressif, les animations décoratives et le comportement legacy qui contredirait `design-taste-frontend` v2.

- [ ] **Step 3: Écrire la feuille de style testable visuellement**

Ajouter les tokens et primitives suivantes dans `globals.css` :

```css
:root {
  --atlas-ink: #122126;
  --atlas-land: #eef0e8;
  --atlas-water: #244d59;
  --atlas-marker: #a45b20;
}

.atlas-grid { background-image: linear-gradient(...); }
.survey-line { transform-origin: left; }
@media (prefers-reduced-motion: no-preference) {
  .atlas-point:hover .survey-line,
  .atlas-point:focus-within .survey-line { transform: scaleX(1); }
}
```

Les motifs portent `aria-hidden="true"` dans le JSX ou sont uniquement des pseudo-éléments décoratifs. Remplacer les anciennes classes de dossier plutôt que d'empiler une seconde direction.

- [ ] **Step 4: Vérifier le mouvement réduit**

Run: `rg -n 'prefers-reduced-motion|animation|transition' app/web/app/globals.css`

Expected: toute transition introduite est neutralisée dans le media query réduit ; aucun mouvement n'est le seul porteur d'information.

- [ ] **Step 5: Consigner la décision**

Ajouter une entrée datée dans `docs/journal-decisions.md` : atlas cadastral local retenu ; cartes distantes et imagerie satellite écartées car elles simuleraient une précision géographique absente des données.

- [ ] **Step 6: Commit**

```bash
git add app/web/app/globals.css DESIGN.md docs/journal-decisions.md
git commit -m "style(web): etablir l'atlas cadastral"
```

### Task 2: Recomposer l'accueil autour de la convergence des sources

**Files:**
- Modify: `app/web/app/page.tsx`
- Modify: `app/web/components/site-shell.tsx`
- Modify: `app/web/app/globals.css`

**Interfaces:**
- Consumes: `CasDemonstration`, `EchelleDpe`, les primitives Atlas de Task 1.
- Produces: un accueil qui explique DVF+, DPE, rapprochement et la limite de Concorde avant l'accès aux cas.

- [ ] **Step 1: Définir le test de contenu par inspection statique**

Run:

```bash
rg -n 'Deux bases publiques|n.estime aucun prix|DVF\+|DPE|Rapprochement' app/web/app/page.tsx
```

Expected: les trois définitions et la limite de non-tarification sont présentes dans la page ; l'accueil ne dépend d'aucune donnée inventée.

- [ ] **Step 2: Remplacer le héros par un point de convergence**

Introduire un décor local décoratif à deux traces (DVF+ et DPE) qui convergent vers une annotation « rapprochement à vérifier ». Conserver le `h1`, le `Link` d'ancrage, les définitions en `dfn` et le `aside` de limite. Exemple de structure :

```tsx
<div className="convergence-map" aria-hidden="true">
  <span className="source-marker source-dvf">DVF+</span>
  <span className="survey-line" />
  <span className="source-marker source-dpe">DPE</span>
  <span className="convergence-marker" />
</div>
```

Les libellés accessibles restent dans le texte réel, afin que ce schéma ne soit jamais nécessaire pour comprendre la page.

- [ ] **Step 3: Transformer les cas en points d'atlas**

Garder exactement la récupération `obtenirDemonstrations()` et les liens vers `/resultat/[id]`. Réorganiser chaque `article` pour présenter le lieu et le bien d'abord, puis DPE et confiance, puis le lien ; l'identifiant de mutation reste absent de l'affichage public.

- [ ] **Step 4: Vérifier la page hors service**

Lancer la page sans API locale ou avec `CONCORDE_API_KEY` absente dans un environnement de test manuel. Expected: un `role="alert"` explique l'indisponibilité ; aucune exception brute n'est rendue.

- [ ] **Step 5: Commit**

```bash
git add app/web/app/page.tsx app/web/components/site-shell.tsx app/web/app/globals.css
git commit -m "feat(web): cartographier les rapprochements"
```

### Task 3: Faire du résultat une lecture de convergence explicable

**Files:**
- Modify: `app/web/components/resultat.tsx`
- Modify: `app/web/app/resultat/[id]/page.tsx`
- Modify: `app/web/app/globals.css`

**Interfaces:**
- Consumes: `DetailRapprochement`, `Verdict`, `profil` et les primitives Atlas.
- Produces: un résultat accessible où les trois axes, les motifs et les réserves constituent des annotations de la conclusion.

- [ ] **Step 1: Écrire le test de régression de profil**

Vérifier dans la route existante que l'identifiant de mutation est conservé quand `profil` change :

```bash
rg -n 'profil|idMutation|Resultat' app/web/app/resultat/\[id\]/page.tsx app/web/components/resultat.tsx
```

Expected: le lien vers l'autre profil conserve le même chemin `/resultat/<id>` et modifie seulement `?profil=`.

- [ ] **Step 2: Ajouter le repère de convergence accessible**

Rendre un graphique de liaison décoratif via CSS, avec une synthèse textuelle adjacente. La conclusion conserve `aria-live="polite"`; le graphique est `aria-hidden` et ne masque pas les noms, scores, unités ou réserves.

- [ ] **Step 3: Réordonner les annotations**

Présenter dans cet ordre : conclusion ; cohérence/anomalie/confiance ; DPE ; motifs et réserves ; aléas ; détail analyste. Ne pas changer les valeurs, leurs labels API ni le POST `/predict`.

- [ ] **Step 4: Vérifier l'annonce et le contenu analyste**

Run:

```bash
rg -n 'aria-live="polite"|id_mutation|id_rapprochement|version du modèle' app/web/components/resultat.tsx
```

Expected: l'annonce du résultat demeure en place ; les identifiants restent limités au profil analyste.

- [ ] **Step 5: Commit**

```bash
git add app/web/components/resultat.tsx app/web/app/resultat/\[id\]/page.tsx app/web/app/globals.css
git commit -m "feat(web): annoter la conclusion du rapprochement"
```

### Task 4: Tracer la méthode et rendre la transparence consultable comme une légende

**Files:**
- Modify: `app/web/app/comment-ca-marche/page.tsx`
- Modify: `app/web/app/transparence/page.tsx`
- Modify: `app/web/app/globals.css`

**Interfaces:**
- Consumes: volumes réels de la chaîne, `Regle[]`, `FicheModele` et les appels serveur existants.
- Produces: deux pages qui rendent visible le parcours des données et la politique appliquée sans recopier les règles.

- [ ] **Step 1: Écrire le test de conservation des sources de vérité**

Run:

```bash
rg -n 'obtenirRegles|obtenirFicheModele|1735|922|716|206' app/web/app/comment-ca-marche/page.tsx app/web/app/transparence/page.tsx
```

Expected: Transparence utilise toujours les deux fonctions serveur ; les volumes affichés sont les volumes vérifiés de la spécification.

- [ ] **Step 2: Recomposer la chaîne comme traversée d'atlas**

Passer de quatre blocs identiques à une séquence de repères numérotés avec trajectoire et libellé de transformation. Le contenu reste compatible avec une lecture verticale au clavier et mobile.

- [ ] **Step 3: Rendre les règles comme légende**

Conserver `article`, `h3`, `dl` et le texte de justification, mais appliquer une grille de légende : identifiant et libellé, seuil et gravité, justification. Les classes n'emploient pas la couleur seule pour la gravité.

- [ ] **Step 4: Vérifier les erreurs serveur**

Run:

```bash
rg -n 'role="alert"|obtenirRegles|obtenirFicheModele' app/web/app/transparence/page.tsx
```

Expected: les indisponibilités de l'API conservent une erreur accessible et ne remplacent pas les données par des règles codées en dur.

- [ ] **Step 5: Commit**

```bash
git add app/web/app/comment-ca-marche/page.tsx app/web/app/transparence/page.tsx app/web/app/globals.css
git commit -m "feat(web): tracer la methode et les regles"
```

### Task 5: Contrôler le rendu, la sécurité et la cohérence finale

**Files:**
- Modify: `.impeccable/config.json` seulement si une exception étroite est un faux positif démontrable.

**Interfaces:**
- Consumes: build de production et les quatre écrans finis.
- Produces: preuves de build, inspection et traitement des signaux Impeccable.

- [ ] **Step 1: Construire le front de production**

Run: `cd app/web && bun run build`

Expected: code de sortie 0, sans police téléchargée.

- [ ] **Step 2: Démarrer et inspecter les quatre écrans**

Run: `cd app/web && bun run start -- --port 3001`

Inspecter `/`, `/resultat/<cas-de-demonstration>`, `/comment-ca-marche`, `/transparence` aux largeurs desktop, 320 px et avec mouvement réduit. Vérifier au clavier le lien d'évitement, chaque lien, le focus et l'absence de débordement horizontal.

- [ ] **Step 3: Vérifier les garde-fous statiques**

Run:

```bash
rg -n 'NEXT_PUBLIC.*KEY|next/font/google|https?://' app/web/app app/web/components app/web/lib || true
git diff --check
```

Expected: aucune clé publique ni police Google ; les seules URL `127.0.0.1` sont dans `lib/concorde.ts`, importé par `server-only`.

- [ ] **Step 4: Passer Impeccable et trier les signaux**

Lancer le détecteur manuel Impeccable sur `app/web`. Corriger les vrais problèmes. Pour un faux positif certain, n'ajouter qu'un `ignore-value` ciblé avec une justification ; ne jamais ignorer un fichier ou une règle complète sans accord utilisateur.

- [ ] **Step 5: Mettre à jour le DESIGN.md**

Documenter le système final effectivement rendu : tokens, hiérarchie, composant de convergence, mouvement, responsive et contraintes hors ligne. Retirer les phrases qui décrivent encore le dossier d'expertise.

- [ ] **Step 6: Commit**

```bash
git add app/web DESIGN.md .impeccable/config.json
git commit -m "style(web): verifier l'atlas hors ligne"
```

## Self-review

- Couverture de la spécification : Task 1 fixe le langage et le mouvement ; Task 2 couvre la compréhension immédiate ; Task 3 couvre les résultats ; Task 4 couvre les deux pages explicatives ; Task 5 couvre build, sécurité, accessibilité et Impeccable.
- Aucun placeholder, comportement fictif ou nouvelle dépendance n'est prévu.
- Les contrats `CasDemonstration`, `DetailRapprochement`, `Verdict`, `Regle` et `FicheModele` restent inchangés dans toutes les tâches.
