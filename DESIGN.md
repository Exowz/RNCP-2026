# Design system - Concorde web

## Lecture du produit

Second client Next.js d'un service public de données : Concorde indique si une
vente DVF+ et un DPE peuvent raisonnablement décrire le même logement. Il ne
vend pas de bien, n'estime aucun prix et rend l'incertitude lisible avant toute
conclusion.

## Direction : Atlas cadastral de preuve

L'interface n'est ni un tableau de bord ni un dossier administratif. C'est un
atlas de lecture : deux trajectoires de sources convergent vers une emprise
abstraite, puis la conclusion est annotée par ses motifs, ses réserves et ses
limites. Les schémas sont des repères visuels locaux ; ils ne représentent jamais
une parcelle réelle ni une géolocalisation de l'utilisateur.

Réglages retenus : variance 4/10, mouvement 3/10, densité 5/10. Le contexte
public, réglementé et accessible limite volontairement les effets expressifs.

## Couleurs

- Terre minérale `#f4f5f0` : fond clair et grille de lecture.
- Encre atlas `#10202c` : titres et texte principal.
- Eau profonde `#183a4d` : action et liaison de source.
- Bleu topographique `#315f7a` : information secondaire.
- Marqueur de vérification `#a86417` : cible, focus et appel à la prudence.
- Alerte `#8f332e` : indisponibilité lisible avec un libellé explicite.

Le mode sombre respecte la préférence système avec les mêmes rôles. L'ambre est
le seul accent, mais aucun statut ne dépend de la couleur seule.

## Typographie et composition

- Titres : pile sérif locale `Georgia, Times New Roman, serif`, réservée au
  raisonnement et aux conclusions ; aucun téléchargement de police.
- Texte : pile système disponible hors ligne ; données techniques en monospace
  système.
- Chaque page utilise une grille asymétrique seulement lorsque celle-ci exprime
  une convergence. Les listes de cas et de règles passent en colonne à 52 rem,
  puis restent sans débordement à 20 rem.
- Les cartes décoratives, badges, ombres et grilles de métriques sont écartés.
  Une ligne, un point ou un trait ne sert qu'à organiser une information réelle.

## Composants et interaction

- Le repère de marque est une construction CSS locale : deux champs et un point
  de rapprochement, sans logo externe ni SVG décoratif.
- Les schémas de convergence sont `aria-hidden`; les explications DVF+, DPE,
  rapprochement et refus d'estimation sont toujours présentes dans le texte.
- Les boutons sont rectangulaires, contrastés et donnent un retour tactile à
  l'activation. Le focus ambre est visible partout.
- Les lignes de source s'étendent légèrement au survol quand le mouvement est
  autorisé. Elles restent immobiles sous `prefers-reduced-motion` et ne portent
  jamais seules le sens.

## Garde-fous

Conserver `lang="fr"`, le lien d'évitement, les repères sémantiques, le résultat
en `aria-live="polite"`, les erreurs `role="alert"` et les appels API côté
serveur. Ne pas introduire de CDN, police distante, image distante, `next/font/google`,
clé `NEXT_PUBLIC_*`, animation infinie, gradient marketing, carte réelle, chiffre
inventé, bouton arrondi, ou changement d'IA.
