# Atlas cadastral — design du front Concorde

## Objectif

Faire comprendre, sans médiation orale, que Concorde confronte deux descriptions
publiques d'un logement et qualifie la fiabilité de leur rapprochement. Le front
Next.js reste un second client de l'API : il n'est ni une interface de saisie
immobilière, ni un estimateur de prix, ni un tableau de bord générique.

## Direction visuelle

La direction « dossier d'expertise » est remplacée par un **atlas cadastral de
preuve**. Le langage de l'interface traduit le geste de Concorde : deux sources
imparfaites convergent vers une même emprise, puis une conclusion explicable.

- Fond minéral clair, encre bleu-noir, vert topographique et ocre de réserve ;
  chaque état est aussi nommé en clair.
- Trame de repérage discrète et motifs de parcelles abstraits, uniquement en CSS
  ou SVG local : aucune carte distante et aucune fausse géolocalisation.
- Grille éditoriale asymétrique, coordonnées, repères et traits de construction
  pour hiérarchiser le contenu ; pas de collection de cartes ni de métriques
  décoratives.
- Titres sérif système, données en monospace système et texte en pile système.
  Aucune police, image ou script distant.

Cette direction est intentionnellement plus spatiale que le précédent dossier,
mais ne prétend jamais montrer la parcelle réelle d'un logement.

## Écrans

### Accueil

Le premier écran présente l'hypothèse : une vente DVF+ et un DPE peuvent être
attribués au même logement sans identifiant commun fiable. Un schéma local à
deux trajectoires conduit vers la conclusion « à vérifier ». La limite « aucune
estimation de prix » est dans le même champ visuel que l'appel à explorer les
cas.

Les cinq démonstrations deviennent des **points d'atlas** : une ligne par cas,
nommée par bien, commune et date. L'étiquette DPE et la confiance ne sont jamais
des codes isolés. Un lien ouvre le résultat sans modifier le calcul.

### Résultat

Le résultat représente la convergence des sources puis expose les trois axes
dans l'ordre de décision : cohérence, anomalie, confiance. Chaque axe inclut sa
lecture verbale. Les réserves, motifs, DPE et aléas sont des annotations de la
conclusion, pas des widgets concurrentiels. Le profil analyste révèle seulement
les identifiants et la décomposition déjà renvoyés par l'API.

### Comment ça marche

La chaîne de préparation est une traversée horizontale de cinq repères : sources
publiques, nettoyage, rapprochement, modèle, contrôle. Les volumes existants
sont des points de passage. Les termes DVF+, DPE et rapprochement restent
définis lors de leur premier emploi.

### Transparence

Chaque règle devient une fiche de légende : libellé humain, identifiant,
seuil, gravité et justification. Les règles continuent de provenir de l'API,
afin que l'interface n'affiche pas une politique différente du code exécuté.

## Mouvement et interaction

Le mouvement est utilitaire et discret : au survol/focus d'un point d'atlas, un
trait de liaison s'étend ; les éléments de la chaîne se révèlent suivant la
lecture ; les changements de profil conservent le cas. Il n'y a ni défilement
parallaxe, ni animation automatique incessante, ni mouvement qui porte une
information.

`prefers-reduced-motion: reduce` désactive toutes ces transitions sans empêcher
la compréhension. Les mêmes retours sont disponibles au clavier par
`:focus-visible`.

## Architecture et limites

La refonte est limitée à `app/web/app`, `app/web/components`, `DESIGN.md` et le
journal de décisions. Elle ne modifie ni les API Python, ni l'application Jinja,
ni les tests Python, ni la CI existante.

Les Server Components et Route Handlers existants restent les seuls à appeler
les services `:8001` et `:8002`. `CONCORDE_API_KEY` demeure une variable sans
préfixe `NEXT_PUBLIC_`; aucun composant client n'appelle les API Python.

## Accessibilité et responsive

Les repères sémantiques, le lien d'évitement, le contraste, l'annonce de
résultat `aria-live`, les erreurs `role=alert` et le focus ocre sont conservés.
Les motifs cadastraux sont décoratifs et masqués des technologies d'assistance.
À 52 rem puis à 20 rem, la carte se transforme en séquence verticale et ne
provoque aucun défilement horizontal.

## Validation

- `bun run build` puis démarrage de production du front ;
- vérification visuelle desktop et mobile, navigation clavier et mouvement réduit ;
- recherche de `NEXT_PUBLIC.*KEY` et `next/font/google` ;
- contrôle qu'aucune dépendance externe n'est requise par le rendu ;
- `git diff --check` ;
- exécution du détecteur Impeccable et traitement explicite de chaque signalement.
