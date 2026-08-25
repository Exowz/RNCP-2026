# Design system — Concorde web

## Direction

Le front est un **dossier d'expertise publique** : il donne à lire une
conclusion, ses preuves et ses limites, plutôt qu'un tableau de bord qui
mettrait des scores en scène. La surface doit pouvoir être comprise par une
personne qui ne connaît ni DVF+ ni le modèle.

## Principes visuels

- Papier chaud, encre vert très sombre, lignes de dossier et une seule couleur
  d'état à la fois ; la couleur ne porte jamais seule le sens.
- Titres en sérif éditoriale (pile locale Georgia), texte et données en pile
  système ; les identifiants techniques restent en monospace seulement quand
  ils sont réellement des données.
- Les informations s'alignent sur des règles horizontales. Les cartes et les
  icônes décoratives sont absentes : une ligne représente un cas, une règle ou
  un constat.
- L'accueil pose immédiatement l'hypothèse vérifiée et la limite « aucune
  estimation de prix ». Le résultat présente les axes comme des conclusions
  accompagnées de leur interprétation.

## Composition

- En-tête sobre : nom, sous-titre factuel, navigation avec soulignement du
  contexte courant.
- Accueil en deux colonnes : thèse et appel à l'action à gauche, limite
  explicite à droite ; la liste de cas est une série de dossiers ouvrables.
- Méthode : chaîne ordonnée en quatre étapes, les chiffres réels étant des
  preuves de parcours et non des métriques décoratives.
- Transparence : chaque règle occupe une ligne avec son identifiant, son seuil,
  sa gravité et sa justification.

## Interaction et accessibilité

Le focus ocre, le lien d'évitement, les repères HTML, les annonces de résultat
et les états d'erreur restent visibles. Les seuls mouvements sont le léger
décalage des lignes de dossier et les transitions de lien ; ils sont désactivés
par `prefers-reduced-motion`. À 52 rem puis 20 rem, toutes les grilles passent
en une colonne sans défilement horizontal.

## Contraintes

Aucun actif distant, aucune police téléchargée et aucun appel API navigateur.
La palette et la typographie sont entièrement disponibles hors ligne.
