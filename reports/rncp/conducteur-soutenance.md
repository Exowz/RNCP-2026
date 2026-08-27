# Conducteur de soutenance RNCP — 1 h 20 + 10 min de questions

Mise à jour : 25 août 2026.

**Règle du référentiel** : une slide ne raconte pas ce qui a été fait, elle **prouve**.
Test de validation : si on retire le titre, le jury doit encore comprendre quelle compétence
est prouvée par la capture ou le résultat affiché.

Bandeau discret sur chaque slide : **Compétences prouvées : Cx, Cy**.

## Budget de temps

| Section | Durée | Cumul |
|---|---:|---:|
| 1. Contexte, problème, ligne de défense | 8 min | 8 |
| 2. Architecture et flux | 8 min | 16 |
| 3. Bloc 1 — données (C1–C5) | 15 min | 31 |
| 4. Bloc 2 — IA, API, MLOps (C6–C13) | 18 min | 49 |
| 5. Bloc 3 — application, CI/CD, MCO (C14–C21) | 18 min | 67 |
| 6. Démonstration live | 8 min | 75 |
| 7. Bilan et limites | 5 min | 80 |

Compter **1,5 à 2 minutes par slide** : viser 45 à 55 slides. Douze slides ne tiennent pas 80 minutes.

---

## 1. Contexte, problème, ligne de défense — 8 min

*Compétences prouvées : cadrage général*

1. **Le problème en une phrase.** Trois bases publiques décrivent le même logement sans
   partager d'identifiant fiable : DVF+ (ventes conclues), DPE (ADEME), Géorisques.
2. **Le piège.** Quand on les croise, le rapprochement peut être faux — **et rien ne le signale**.
3. **Ce que je refuse de faire.** Ni prédiction de prix, ni tarification. Dire pourquoi :
   estimer une solvabilité ferait entrer dans le champ haut risque du règlement IA.
4. **Ligne de défense.** « Je ne remplace pas la décision ; je réduis l'écart entre des données
   complexes et une décision informée, en rendant visibles les sources, les hypothèses et les
   inconnues. »
5. **Deux publics.** Particulier / analyste crédit. → capture `07-web-accueil-le-pourquoi-et-glossaire.jpg`

## 2. Architecture et flux — 8 min

*Compétences prouvées : C15*

6. Schéma global : 5 sources → nettoyage → rapprochement → modèle → 2 APIs → 2 clients.
7. **Les volumes réels** : 1 735 lignes brutes → 922 rapprochements → 716 appariés →
   **206 non évaluables**. → capture `10-web-comment-ca-marche-volumes-reels.jpg`
8. **La contrainte structurante : hors ligne.** Garde-fou au niveau socket, pas une promesse.
9. Pile technique et **pourquoi** chaque brique. *(Ne pas citer ce qu'on n'utilise pas.)*

## 3. Bloc 1 — données — 15 min

*Compétences prouvées : C1, C2, C3, C4, C5*

10. **C1 — les cinq types exigés**, dans un seul manifeste : fichier, big data, service web,
    page web, base de données. Montrer `data/raw/_manifest.json` : empreinte SHA-256, volumes, statut.
11. **C1 — gestion d'erreur** : une source en panne n'interrompt pas les quatre autres.
12. **C2 — SQL PostgreSQL** : la jointure communes × aléas.
13. **C2 — Spark SQL** : l'agrégation DPE. Dire pourquoi Spark ici (10 M de DPE en cible).
14. **C3 — les 10 règles de nettoyage**, chacune **justifiée**.
15. **C3 — le tableau avant/après**, *généré* : chaque règle supprime des lignes réelles.
16. **C3 — dataset versionné par DVC**, remote local.
17. **C4 — MCD et MPD.**
18. **C4 — RGPD** : et l'engagement de minimisation est **vérifié par un test**, pas seulement écrit.
19. **C5 — API data** : 4 routes, authentification par rôle, OpenAPI générée depuis le contrat appliqué.

**Le moment fort** : le tableau avant/après. Il prouve que les règles agissent.

## 4. Bloc 2 — IA, API, MLOps — 18 min

*Compétences prouvées : C6, C7, C8, C9, C10, C11, C12, C13*

20. **C6 — veille** : thématiques, sources qualifiées, décisions. **Annoncer la limite tout de suite.**
21. **C7 — benchmark** : services retenus **et écartés**, dont sobriété et contrainte hors ligne.
22. **C8 — LM Studio local**, `gemma-4-e4b` présent sur disque, doctrine « données structurées
    d'abord, LLM sur le résidu ».
23. **Le modèle : pourquoi un auto-encodeur ?** Aucune étiquette « rapprochement faux » n'existe →
    non supervisé par nature.
24. **Les trois axes, jamais fusionnés** : cohérence, atypicité, confiance.
25. **Pourquoi trois et pas un** — *la question que le jury posera*. Un cas cohérent peut être peu
    fiable ; un cas bizarre peut être bien documenté.
26. **C9 — l'API** : auth, validation stricte, OpenAPI. Montrer un 401 et un 422.
27. **C11 — dérive** (Evidently), latence, erreurs, seuils, alertes.
28. **C12 — 54 tests, 86 % de couverture**, dont robustesse du modèle.
29. **La métrique honnête : AUC 0,9095** pour l'auto-encodeur seul. Expliquer que le rappel des
    règles est **circulaire** et n'est pas présenté comme une performance.
30. **C13 — la chaîne CI complète**, exécutée. → capture `04-ci-github-verte.png`
31. **C13 — la porte de conformité** : 12 critères, 3 axes, **elle bloque le build**.

**Le moment fort** : la slide « pourquoi trois scores séparés ». C'est la thèse du produit.

## 5. Bloc 3 — application, CI/CD, MCO — 18 min

*Compétences prouvées : C14, C15, C16, C17, C18, C19, C20, C21*

32. **C14 — personas et user stories**, critères d'acceptation vérifiables.
33. **C10/C14 — deux clients de la même API** : Jinja et Next.js. Ce qui prouve que l'API est un
    **contrat**, pas un utilitaire de gabarit.
34. **C14/C17 — accessibilité** : lien d'évitement, ARIA, `aria-live`, focus visible.
35. **C17 — contrastes calculés**, ≥ 4,5:1 en clair **et** en sombre.
36. **C17 — sécurité** : rôles, comparaison à temps constant, en-têtes OWASP, secrets hors Git.
37. **C17 — la clé d'API n'atteint jamais le navigateur** (`server-only`).
38. **C10 — dégradation propre** quand l'API tombe. → capture `09-web-degradation-api-indisponible.jpg`
39. **C18 — CI** avec **Bandit** et **pip-audit**.
40. **C19 — livraison** : image Docker, Compose `--no-build`, sonde saine.
41. **C20 — journalisation** : JSON Lines, pseudonymisation **à l'écriture**, `X-Request-ID`
    traversant app → API. → capture `04-surveillance-locale-seuils-alertes.jpg`
42. **C21 — cinq incidents réels.** Une slide de synthèse, puis deux détaillés.
43. **C21 — incident détaillé n°1** : `APP-2026-08-25`, le `405` en pleine démo.
    → capture `06-bascule-profil-corrigee.jpg`
44. **C21 — incident détaillé n°2** : `SEC-2026-08-25-bis`, la porte déclarait conforme une chaîne
    cassée. **Un artefact valide ne prouve que le passé.**
45. **C21 — le motif récurrent** : quatre incidents sur cinq venaient d'une documentation qui
    affirmait ce que le code ne faisait pas.

**Le moment fort** : les incidents. Personne n'a cinq incidents réels avec non-régression vérifiée
dans les deux sens.

## 6. Démonstration live — 8 min

*Compétences prouvées : C10, C14, C17, C20*

**Ordre imposé, répété à l'avance :**

1. Accueil → **« Aucun DPE rapproché »** → le système répond `non évaluable`.
   *« Il refuse de conclure. »*
2. Retour → **« Surfaces incompatibles »** → les trois cartes. *« Contradiction majeure, et j'en suis sûr. »*
3. Bascule **Analyste** → décomposition de l'écart. *« Et voici pourquoi. »*
4. **Transparence** → les règles avec leurs seuils. *« Aucun seuil n'est arbitraire. »*
5. **Surveillance locale** → seuils, alertes, latences.
6. *(si le temps le permet)* Casser un critère → la porte passe **NON CONFORME**, le build est bloqué.

**Avant la démo** : les 4 services démarrés et vérifiés, la fenêtre déjà ouverte,
le build Next déjà fait. On ne construit rien devant le jury.

## 7. Bilan et limites — 5 min

46. **Ce qui est prouvé** : 19 compétences, 2 partielles assumées.
47. **C6 et C16 partiels** — le dire soi-même, avant que le jury le trouve. Ne jamais simuler une équipe.
48. **Limites du modèle** : métriques de règles circulaires, base DPE non représentative,
    rapprochement par parcelle ambigu en copropriété.
49. **Ce que je ferais ensuite** : audit RGAA certifié, image runtime réduite, données réelles à
    l'échelle nationale.
50. **Retour au début** : *« je rends visibles les sources, les hypothèses et les inconnues. »*

---

## Les questions à préparer (10 min)

| Question probable | Réponse en deux phrases |
|---|---|
| Pourquoi un auto-encodeur ? | Aucune étiquette « rapprochement faux » n'existe dans les données publiques : le problème est non supervisé par nature. Et son erreur se décompose par variable, donc il dit *laquelle* est atypique. |
| D'où sort le seuil de 20 % sur les surfaces ? | La surface réelle bâtie (DVF) et la surface habitable (DPE) ne mesurent pas la même chose : un écart modéré est attendu. Au-delà, c'est plus probablement deux logements différents qu'une convention de mesure. |
| Pourquoi trois scores et pas une note ? | Ce sont trois questions différentes. Un rapprochement cohérent peut être peu fiable, un rapprochement bizarre peut être bien documenté ; les fusionner détruit l'information que le produit prétend fournir. |
| Pourquoi pas de GPU ? | Le modèle a 8 variables et 500 lignes : le coût de lancement des noyaux dépasserait le calcul. Et le CPU permet à la CI de réentraîner à l'identique — la reproductibilité valait plus que des millisecondes. |
| C'est de la finance ? | Non, et c'est délibéré. Je produis la couche de fiabilité **en amont** d'une décision ; estimer un prix ou une solvabilité m'aurait fait entrer dans le champ haut risque du règlement IA. |
| Comment gérez-vous les incidents ? | Cinq cas datés, avec reproduction, diagnostic, correctif minimal et non-régression vérifiée dans les deux sens — je retire le correctif pour confirmer que le test échoue bien. |
| Le travail collectif de C6 et C16 ? | Je suis seul, je ne simule aucune équipe. Je montre un pilotage individuel réel et j'assume la couverture partielle ; le volet MLOps de C16, lui, est entièrement couvert. |
| Vos métriques sont-elles fiables ? | L'AUC 0,9095 l'est : l'auto-encodeur n'a vu ni les règles ni les étiquettes. Le rappel des règles est circulaire sur le jeu de démonstration et je ne le présente pas comme une performance. |
| PostgreSQL ou SQLite ? | PostgreSQL porte les données métier, avec son MCD et son import : c'est ma base au sens de C4. `mlflow.db` est le magasin de suivi d'expériences, imposé par MLflow depuis qu'il a déprécié son stockage fichier. |
| Et si Internet tombe ? | Rien ne change : le garde-fou socket interdit toute sortie non locale, les poids du modèle, les données et les images Docker sont présents avant. Je peux couper le Wi-Fi maintenant. |
