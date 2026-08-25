# Pilotage individuel et MLOps — C16

## Cadre honnête

Le projet est réalisé par une seule personne en trois jours. Il ne simule ni
équipe, ni stand-up collectif, ni validation par un rôle inexistant. Les
éléments ci-dessous démontrent une conduite de travail personnelle ; ils ne
couvrent donc que partiellement l'aspect collectif de C16.

## Tableau de pilotage au 25 août 2026

| État | Carte | Preuve de sortie |
|---|---|---|
| Fait | Socle, tranche verticale et Bloc 1 C1–C5 | Scripts, APIs, Spark, PostgreSQL, matrice verte. |
| Fait | Bloc 2 C6–C11 et API modèle C9 | Veille, benchmark, LM Studio local, Evidently, OpenAPI. |
| Fait | C12–C13 | Tests, CI, packaging et livraison d'artefact vérifiés. |
| Fait | Bloc 3 C14–C20 | Spécifications, architecture, sécurité et livraison applicative vérifiées. |
| Fait | Incident C21 | Deux causes CI, correctifs et non-régression GitHub dans `docs/incident.md`. |

La matrice `reports/rncp/matrice-preuves.md` est le tableau de bord de
réalisation : une carte ne passe au vert qu'avec une commande, un log ou une
exécution distante, plus un paragraphe de rapport.

## Rythme et Definition of Done

Chaque demi-journée suit le même cycle : choisir une compétence prioritaire,
écrire ou exécuter la preuve, conserver le log/capture, ajouter le paragraphe
au rapport E1–E5, mettre à jour la matrice, puis créer un commit et un tag si
l'état est démontrable.

Une tâche n'est terminée que si :

1. elle fonctionne sans Internet pour la démo ;
2. elle est couverte par un test ou un log rejouable ;
3. sa décision et sa limite sont écrites dans la documentation ;
4. sa preuve est localisable dans la matrice.

## Risques et décisions prises

| Risque | Réponse retenue | Décision observable |
|---|---|---|
| Dépendance cachée au réseau | Fixtures, poids locaux et garde-fou socket. | Tests hors ligne et démonstration sur `127.0.0.1`. |
| Spark incompatible avec le JDK du poste | Java 17 fixé dans script et CI. | Échec reproduit avec Java 26 ; fonctionnement avec Java 17. |
| CI seulement déclarative | Push public, lecture des logs, correctifs minimaux. | Run GitHub vert et incident C21 documenté. |
| Trop de périmètre en trois jours | Une seule chaîne étroite, deux profils de restitution. | Pas de prédiction de prix, pas de comptes, pas de cloud. |

La rétrospective initiale est déjà documentée dans la section REX de
`docs/incident.md` : l'exécution via `uv run` est maintenant la référence, car
un lancement direct de pytest peut masquer un défaut de packaging.
