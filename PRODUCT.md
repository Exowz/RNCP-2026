# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Une personne qui découvre Concorde — notamment un jury ou un utilisateur non
technique — doit pouvoir comprendre le résultat d'un rapprochement sans
explication orale. Un profil analyste accède en complément aux identifiants et
aux éléments techniques du même calcul.

## Product Purpose

Concorde évalue la fiabilité de l'association entre une vente immobilière issue
de DVF+ et un diagnostic de performance énergétique. Il rend l'incertitude,
les contradictions et les réserves explicites avant toute réutilisation du
rapprochement.

## Positioning

Le produit ne prédit ni prix ni tarification : il vérifie l'hypothèse qu'une
vente et un DPE décrivent le même logement, alors que les deux sources publiques
ne partagent pas d'identifiant fiable.

## Operating Context

La démonstration est locale et hors ligne. Le front Next.js est un second
client des APIs de données et de modèle, tandis que l'application Jinja reste
le livrable évalué principal. Les cas affichés viennent d'une table préparée et
les règles de transparence viennent du code exécuté.

## Capabilities and Constraints

- quatre écrans : accueil, résultat, méthode et transparence ;
- appels API uniquement côté serveur Next.js avec une clé non publique ;
- aucun CDN, aucune image ou police distante ;
- contenu français, navigation au clavier, focus visible, contraste minimum
  4,5:1 et respect de `prefers-reduced-motion` ;
- le profil change la restitution, jamais le calcul ;
- les identifiants de contrat API restent en ASCII.

## Brand Commitments

Le nom Concorde, un ton rigoureux et pédagogique, et l'affirmation explicite
de ce que le produit refuse de faire sont à préserver.

## Evidence on Hand

Les cas pédagogiques, le verdict, les règles et la fiche modèle sont fournis
par les APIs locales. Les volumes réels de la chaîne et les textes explicatifs
sont documentés dans `docs/specs-frontend-web.md`.

## Product Principles

1. Montrer le monde réel avant les identifiants techniques.
2. Faire voir les limites et l'incertitude au même niveau que le verdict.
3. Distinguer une preuve d'un score décoratif.
4. Préserver la compréhension hors ligne et sans accompagnement oral.

## Accessibility & Inclusion

Le front respecte la parité d'accessibilité de l'application existante : langue
française, repères sémantiques, lien d'évitement, clavier, focus visible,
contrastes suffisants, messages d'erreur annoncés et mouvement réduit.
