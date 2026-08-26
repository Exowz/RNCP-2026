# Script de soutenance — Concorde

**27 août 2026, 14h00–16h30, distanciel.** Présentation Gamma unique, 64 slides.

Numérotation **alignée sur le deck**. Rythme visé ~135 mots/minute.
La colonne **É** indique l'épreuve à laquelle la slide se rattache, pour le bandeau.

> **Avant de te connecter** : `./scripts/soutenance.sh start` — code de sortie 0 = tout est prêt.
> **Après la démo de l'application** (où tu arrêtes l'API) : `./scripts/soutenance.sh api-model`

---


## 1. Concorde — page de titre

`Épreuve E1`

Bonjour. Je vais vous présenter Concorde, et cette première épreuve porte sur la couche de
données : comment je collecte, comment je nettoie, comment je stocke, comment je mets à
disposition. Avant d'entrer dans la technique, je voudrais expliquer le choix du sujet, parce
qu'il commande tout ce qui suit.


---


## 2. Le fil de cette soutenance

`Épreuve —`

Avant d'entrer dans le détail, voici le fil que je vais suivre. Ce n'est pas le déroulé
administratif des épreuves, que vous connaissez mieux que moi : c'est l'enchaînement de mon
raisonnement, en six temps.

Je pars d'un problème que rien ne signale. Je montre ensuite une chaîne de données qui compte ce
qu'elle jette, puis un modèle qui refuse de conclure quand il ne peut pas, une application qui
montre ses inconnues, un service d'IA que j'ai mesuré avant de le croire, et enfin cinq incidents
réels.

Un fil rouge traverse les six : **une preuve qui n'est pas exécutée n'est pas une preuve.** Vous
verrez que c'est aussi ce que ce projet m'a appris de plus utile.


---


## 3. Pourquoi ce sujet

`Épreuve E1`

Je suis admis en Master AI and Data for Finance pour la rentrée. Je voulais donc un projet qui
me prépare réellement à ce secteur, et pas un exercice hors sol.

Le réflexe aurait été de faire de la prédiction : estimer un prix au mètre carré, scorer un
risque. Je ne l'ai pas fait, et c'est un choix délibéré que j'assume complètement.

La raison est simple. En finance, un modèle de risque ne vaut jamais mieux que les données qu'on
lui donne. On peut construire le meilleur modèle du monde : si ses entrées sont fausses, sa
sortie l'est aussi, et rien ne le signale. Le problème que j'ai trouvé le plus intéressant, et
le plus utile, est donc celui d'avant : quand on croise plusieurs sources publiques pour nourrir
une décision, comment sait-on que le croisement est juste ?

C'est le travail dont dépend tout le reste, et c'est celui qu'on saute le plus souvent. J'ai
préféré le traiter à fond plutôt que d'ajouter une couche prédictive que je n'aurais pas pu
valider sérieusement en trois jours.


---


## 4. Le terrain : trois bases, aucune clé commune

`Épreuve E1` · 📷 **capture : `12-web-accueil-atlas-schema-dvf-dpe.jpg`**

Le terrain, c'est l'immobilier, parce qu'il réunit trois bases publiques riches et
structurellement mal reliées.

DVF+ recense les ventes déjà conclues, issues des actes notariés — attention, ce ne sont pas les
biens en vente. Les DPE de l'ADEME donnent l'étiquette énergétique. Géorisques donne l'exposition
aux aléas naturels.

Ces trois bases décrivent le même parc et ne partagent aucun identifiant commun fiable. Quand
vous rapprochez une vente et un diagnostic, vous formulez une hypothèse — vous ne constatez pas
un fait. Et personne ne vous dit quand l'hypothèse est fausse.

Le lien avec la finance est direct. Une banque qui accorde un prêt immobilier prend le logement
en garantie. Un bien classé G est aujourd'hui frappé d'interdiction de location et d'obligation
de rénovation : sa valeur de garantie change. Si l'étiquette énergétique vient d'un rapprochement
erroné, la banque a mal évalué son collatéral, et elle ne le sait pas.

Concorde ne prend pas cette décision à sa place. Il lui dit à quel point elle peut se fier à la
donnée sur laquelle elle s'apprête à la prendre.


---


## 5. Le lien avec la finance est direct

`Épreuve E1`

Le lien avec la finance est direct, et je veux le rendre concret.

Une banque qui accorde un prêt immobilier prend le logement en garantie. Or un bien classé G est
aujourd'hui frappé d'interdiction de location et d'obligation de rénovation : **sa valeur de
collatéral change réellement.**

Si l'étiquette énergétique qu'elle utilise vient d'un rapprochement erroné, la banque a mal évalué
sa garantie — et surtout, elle l'ignore. Rien dans la donnée ne le lui dit.

Concorde ne prend pas cette décision à sa place. Il lui dit à quel point elle peut se fier à la
donnée sur laquelle elle s'apprête à la prendre. C'est une nuance, mais c'est toute la différence
entre un outil d'aide et un outil qui décide.


---


## 6. Ce que Concorde fait, et ne fait pas

`Épreuve E1`

Voici ce que fait Concorde, en trois questions volontairement séparées.

La cohérence demande si les deux enregistrements se contredisent. L'anomalie demande si ce
rapprochement ressemble aux autres. La confiance demande si l'on peut se fier à la réponse
elle-même.

Elles ne sont **jamais fusionnées en une note unique**, et c'est un choix de conception. Un
rapprochement peut être parfaitement cohérent et malgré tout peu fiable, parce qu'il manque la
moitié des champs. Un autre peut être atypique tout en étant parfaitement documenté. Les fusionner
détruirait exactement l'information que le produit prétend fournir.

Et Concorde n'estime aucun prix. Ce n'est pas une limite technique : estimer une valeur ou une
solvabilité ferait entrer le projet dans le champ haut risque du règlement européen sur l'IA, avec
des obligations que je ne peux pas honorer sur ce périmètre.


---


## 7. SECTION — Données

`Épreuve E1`

Premier bloc : la couche de données. Comment je collecte, comment je nettoie, comment je stocke, et comment je mets à disposition.


---


## 8. La chaîne, avec ses volumes réels

`Épreuve E1`

Voici la chaîne complète, avec les volumes de la dernière exécution — ce sont des chiffres réels,
régénérables devant vous en une trentaine de secondes.

Six collecteurs couvrant cinq types de sources produisent 1 743 lignes brutes. Dix règles de
nettoyage en retirent une partie. Le rapprochement produit 922 candidats, dont 716 sont appariés
à un diagnostic. Deux cent six ne le sont pas, et je les conserve. Quarante-quatre parcelles
portent plusieurs diagnostics, donc le rapprochement y est ambigu.

Ces deux derniers chiffres sont le cœur du produit, j'y reviendrai.


---


## 9. C1 — Un contrat unique pour cinq types de sources

`Épreuve E1`

Le référentiel demande d'automatiser l'extraction depuis cinq types de sources : fichier, service
web, page web, base de données et système big data.

Le premier réflexe serait d'écrire cinq scripts. J'ai fait l'inverse : une classe abstraite
définit le contrat, et chaque source n'implémente qu'une méthode, qui renvoie un tableau de
données. Le socle mutualise tout le reste — le point d'entrée, la journalisation, la gestion
d'erreur, l'écriture sur disque, l'inscription au manifeste.

Concrètement, ajouter une sixième source coûte une vingtaine de lignes, et elle hérite
automatiquement des garanties des cinq autres. C'est ce qui fait une chaîne homogène plutôt que
cinq scripts qui se ressemblent vaguement.


---


## 10. C1 — Les cinq types, prouvés par le manifeste

`Épreuve E1`

Et voici la preuve. À chaque collecte, le socle écrit une entrée dans un manifeste : le type,
l'origine, le nombre de lignes, la taille, la durée, l'horodatage, et une empreinte SHA-256 du
fichier produit.

Ce manifeste n'est pas de la documentation, c'est un artefact généré, et il prouve trois choses
d'un coup. Les cinq types exigés sont présents, ligne par ligne. Les volumes sont réels. Et
l'empreinte permet de vérifier qu'un fichier n'a pas changé entre deux exécutions.

C'est ce qui rend la chaîne vérifiable et non pas seulement racontée. La commande est
`python -m concorde.collect`.


---


## 11. C1 — Une source en panne n'arrête pas les autres

`Épreuve E1`

Le référentiel demande une gestion d'erreur. J'ai fait un choix précis : une source qui échoue
ne remonte pas son exception jusqu'à interrompre le programme. Elle est journalisée, inscrite au
manifeste comme échec, et la collecte continue.

La raison est opérationnelle. Si l'API de la Base Adresse Nationale est indisponible un matin,
je veux récupérer mes quatre autres sources, et savoir exactement laquelle a échoué et pourquoi.

L'exemple affiché est réel. Il vient d'une exécution où le schéma du fichier DVF n'était pas
celui attendu : le message nomme les six colonnes manquantes. Détecter ça à la collecte coûte une
seconde ; le détecter après le nettoyage coûte une heure.


---


## 12. C2 — Requête SQL sur le SGBD

`Épreuve E1`

Le référentiel demande des requêtes SQL documentées, avec leurs jointures, leurs filtres et
leurs optimisations. En voici une.

Quatre choix. Le `LEFT JOIN` conserve les communes sans aléa recensé : un `INNER JOIN` les ferait
disparaître silencieusement, et je croirais qu'une commune sans aléa n'existe pas. Le `COALESCE`
traduit cette absence en zéro, pour que le code appelant n'ait pas deux cas à gérer. Le `FILTER`
compte les aléas significatifs dans le même passage, au lieu d'une seconde requête. Et le
paramètre est une valeur liée, jamais concaténée : c'est ce qui empêche l'injection SQL.

La requête est couverte par un test.


---


## 13. C2 — Requête sur le système big data

`Épreuve E1`

Le référentiel exige aussi une requête sur un système big data, et c'est là que Spark intervient.

Je veux devancer la question, parce qu'elle est légitime : sur mon extrait de 726 lignes, Spark
n'apporte rien. Pandas serait plus rapide. Le choix se justifie par la cible : la base DPE de
l'ADEME dépasse dix millions d'enregistrements. À cette échelle, le traitement ne tient plus en
mémoire sur une machine et l'agrégation doit être distribuée. J'ai donc écrit la chaîne avec
l'outil de la cible, pas avec celui du prototype.

Deux réglages pour que la démonstration reste légère : une seule partition, et la session est
explicitement arrêtée après lecture pour ne pas laisser une machine virtuelle Java en arrière-plan.


---


## 14. C3 — Des règles nommées, comptées, justifiées

`Épreuve E1`

Le nettoyage. Le référentiel demande des règles écrites, la suppression des entrées corrompues,
et un tableau avant-après.

J'aurais pu enchaîner des filtres pandas. Le problème, c'est qu'au bout de dix filtres, plus
personne ne sait lequel a supprimé quoi ni pourquoi.

Chaque règle est donc un objet, qui porte un identifiant, un libellé, une justification métier
rédigée, et le filtre lui-même. Le moteur les exécute dans l'ordre et compte, pour chacune, les
lignes entrantes et sortantes. Conséquence : le tableau que je vais montrer est généré. Il ne
peut pas diverger du code, puisqu'il est produit par lui.


---


## 15. C3 — Le tableau avant / après

`Épreuve E1`

Voici le tableau. Chaque ligne est une règle, et chaque règle supprime des lignes réelles.

J'insiste sur un point facile à rater : ce ne sont pas des règles décoratives écrites pour cocher
une case. La règle 4 retire vingt-cinq dépendances et locaux commerciaux, parce qu'un garage n'a
pas de diagnostic énergétique de logement comparable : le rapprocher produirait du bruit, pas de
l'information. La règle 5 supprime dix-huit doublons — dans DVF, une mutation à plusieurs
dispositions apparaît plusieurs fois, et sans déduplication le même bien pèserait plusieurs fois
dans mes statistiques.

Au total je retire près de dix pour cent des lignes DVF, et je peux justifier chaque suppression
individuellement.


---


## 16. C3 — Ce que le rapprochement ne sait pas

`Épreuve E1`

Le rapprochement se fait sur la parcelle cadastrale, seul identifiant partagé entre DVF et
l'adressage des DPE. Ce choix est discutable, et c'est précisément le sujet du projet.

Il est fiable quand une parcelle porte un seul logement, et ambigu dès qu'elle en porte
plusieurs — en copropriété. Quarante-quatre parcelles sont dans ce cas. Je ne masque pas cette
ambiguïté : je la compte, je la stocke dans une colonne, et elle fera baisser le niveau de
confiance en aval.

Et deux cent six mutations n'ont aucun diagnostic rapprochable. Je les conserve. J'aurais pu les
supprimer pour présenter un jeu plus propre — j'ai fait l'inverse, parce que l'absence
d'information est une information, et qu'un système honnête doit pouvoir répondre « je ne sais
pas ».


---


## 17. C4 — Modèle de données et RGPD vérifié

`Épreuve E1`

Pour le stockage, PostgreSQL en conteneur : un SGBD relationnel complet, qui permet de vraies
jointures, et une installation reproductible sur n'importe quelle machine. Le modèle conceptuel
et physique sont documentés. Le script d'import est idempotent : je peux le rejouer sans créer
de doublons.

Sur le RGPD, je voudrais vous montrer une chose. J'ai un registre classique — finalité, base
légale, minimisation, conservation, sécurité. Il engage Concorde à ne publier aucune adresse
détaillée, parce que croiser une adresse précise, un prix de vente et une étiquette énergétique
permet de désigner un logement, donc potentiellement son occupant.

Le problème, c'est qu'un registre est un document, et que rien n'empêche le code de s'en écarter.
C'est exactement ce qui m'est arrivé : en ajoutant des routes à l'API, j'ai exposé sans le
vouloir le champ adresse. Le registre disait une chose, le code en faisait une autre.

J'ai corrigé, et surtout j'ai écrit ce test. Il interroge les trois routes et échoue si une
adresse réapparaît. L'engagement n'est plus une intention : c'est une contrainte vérifiée à
chaque exécution.


---


## 18. C5 — L'API de mise à disposition

`Épreuve E1`

Dernier point : la mise à disposition, par cinq routes REST.

Trois éléments sur cette signature. Le paramètre est contraint par une expression régulière —
deux chiffres, rien d'autre : une entrée non conforme est rejetée avant d'atteindre le code
métier, avec un message qui nomme le champ fautif. La dépendance `exige_role` impose une clé
d'API valide et un rôle suffisant : sans clé, la route répond 401, et je peux vous le montrer en
direct. Enfin, la documentation OpenAPI est générée à partir de ces annotations : elle décrit
donc le contrat réellement appliqué, pas un document rédigé à côté qui pourrait dériver.


---


## 19. SECTION — Modèle et MLOps

`Épreuve E3`

Deuxième bloc : la mise en service du modèle et la chaîne MLOps. Il se termine par une démonstration.


---


## 20. Le cadre imposé, et la mise en scène assumée

`Épreuve E3`

Cette épreuve suppose un modèle fourni et une application existante. Mon dépôt est neuf, donc
j'assume une mise en scène honnête : je me place à la frontière entre deux équipes. L'équipe Data
Science livre un artefact PyTorch gelé et versionné, accompagné de sa fiche ; l'équipe applicative
le met en service.

Cette frontière n'est pas décorative : elle est matérialisée par un fichier unique, `concorde_moteur.pt`,
qui contient tout ce qu'il faut pour rejouer une prédiction à l'identique. J'y reviens dans deux slides.


---


## 21. Pourquoi un auto-encodeur

`Épreuve E3`

Pourquoi un auto-encodeur, et pas une classification ? Parce qu'il n'existe aucune étiquette
« ce rapprochement est faux » dans les données publiques. Personne n'a annoté les appariements.
Le problème est donc non supervisé par nature.

Le principe : le réseau apprend à comprimer puis reconstruire la structure majoritaire des
rapprochements. Ce qu'il reconstruit mal est, par construction, ce qui ne ressemble pas au reste.

Deux choix d'architecture méritent une justification. Le goulot est volontairement étroit — trois
dimensions : un réseau plus large mémoriserait les anomalies au lieu de les manquer, et l'erreur
de reconstruction s'effondrerait précisément sur les lignes que je cherche à isoler. Et
l'entraînement s'arrête par arrêt anticipé sur la perte de validation, pour la même raison : un
auto-encodeur trop entraîné finit par reconstruire correctement les anomalies, et perd sa raison
d'être.

Dernier point qui compte pour l'explicabilité : l'erreur se décompose **par variable**. Le modèle
ne dit pas seulement « cette ligne est atypique », il dit **quelle dimension** l'est.


---


## 22. La métrique honnête

`Épreuve E3`

Voici les métriques, et je veux être précis sur ce qui est informatif et ce qui ne l'est pas.

Le jeu de démonstration porte des anomalies plantées, et mes règles de cohérence visent les mêmes
familles de contradictions. Le rappel des règles est donc **circulaire** : il mesure la cohérence
de mon générateur avec lui-même, pas une performance. Je le publie par transparence, et je ne le
présente jamais comme un résultat.

La métrique informative est l'AUC de l'auto-encodeur seul : 0,91. Elle l'est parce que
l'auto-encodeur n'a vu ni les règles, ni les étiquettes — il n'a appris que la structure des
données. Un pouvoir de tri de 0,91 sur un problème non supervisé est un bon résultat.

Détail intéressant : l'auto-encodeur trie mieux que mes règles ne rappellent. Autrement dit,
l'apprentissage attrape des choses que je n'avais pas prévues en écrivant les règles. C'est
exactement ce qu'on lui demande.


---


## 23. Les cinq règles, et d'où viennent leurs seuils

`Épreuve E3`

Je veux détailler les règles, parce que « seuillé » ne veut rien dire si les seuils sortent de
nulle part.

La première tolère 20 % d'écart entre la surface déclarée à la vente et la surface habitable du
diagnostic. Pourquoi 20 ? Parce que ces deux notions ne mesurent pas la même chose : les combles,
les sous-sols et les annexes comptent dans l'une et pas dans l'autre. Un écart modéré est donc
**attendu**. Au-delà du seuil, l'explication la plus probable n'est plus une convention de mesure,
c'est que les deux enregistrements décrivent deux logements différents.

La quatrième est la plus facile à défendre : dix ans, c'est la durée de validité réglementaire
d'un DPE. Le seuil n'est pas un choix, c'est le droit.

La cinquième est celle qui touche au prix, et je précise immédiatement : le prix n'est **pas
prédit**. Il sert uniquement de signal de cohérence. Un écart extrême à la médiane communale
signale généralement une mutation qui n'est pas une vente ordinaire — un viager, un démembrement,
une vente entre proches — plutôt qu'un bien exceptionnel.

Enfin, les pondérations. Un motif majeur retire 0,40 à la cohérence, un mineur 0,15. Deux motifs
majeurs suffisent donc à faire tomber le score à 20 %. C'est délibéré : deux contradictions
sérieuses ne se compensent pas, elles s'additionnent.


---


## 24. L'artefact gelé : tout ce qu'il faut pour rejouer

`Épreuve E3`

L'artefact contient tout : les poids, mais aussi les paramètres de normalisation, les médianes
d'imputation, les médianes de prix communales de référence, la grille de calibration, et une fiche
d'identité avec la version, la graine aléatoire, l'empreinte du jeu d'entraînement et le commit Git.

Un point de méthode : les médianes communales sont **figées** dans l'artefact, calculées sur
l'entraînement seul. Les recalculer à l'inférence ferait dépendre le score du lot de production —
c'est une fuite, et cela rendrait la prédiction non reproductible.

Et il y a un garde-fou au chargement : si le contrat de variables de l'artefact ne correspond
plus au code, le service refuse de démarrer avec un message explicite plutôt que de servir des
prédictions silencieusement fausses.

Conséquence directe : servir le modèle ne demande aucun accès réseau. C'est ce qui rend la
démonstration hors ligne possible.


---


## 25. C9 — L'API qui expose le modèle

`Épreuve E3`

L'API expose le modèle par six routes. Trois éléments sur celle-ci.

`exige_role("reader")` impose une clé d'API valide et un rôle suffisant. Sans clé, la réponse est
401 — je vous le montrerai.

`extra="forbid"` : un champ inconnu dans la charge utile est une erreur, pas un silence. J'ai fait
ce choix volontairement, parce qu'un service qui « répare » discrètement une entrée douteuse
produit un résultat que plus personne ne peut expliquer ensuite. C'est exactement le défaut que
Concorde cherche à rendre visible chez les autres : je ne pouvais pas le commettre moi-même.

Et `moteur_requis` : si l'artefact est absent, le service démarre quand même, se déclare
« dégradé » sur sa sonde de santé, et répond 503 avec la commande exacte à exécuter. Un service
qui refuse de démarrer ne dit pas ce qui lui manque ; celui-ci le dit.


---


## 26. C10 — Deux clients indépendants de la même API

`Épreuve E3` · 📷 **capture : `09-web-degradation-api-indisponible.jpg`**

L'intégration, maintenant. Deux applications consomment cette API : une application rendue côté
serveur en Jinja, et un front Next.js. Aucune des deux n'importe le moteur — toutes deux passent
par HTTP.

Ce n'est pas de la redondance gratuite. Une API consommée par deux clients indépendants cesse
d'être un utilitaire de gabarit et devient un contrat : le découplage que j'annonce est
démontrable, pas déclaré.

Et j'ai testé la panne. Quand j'arrête l'API modèle, l'application n'affiche ni trace technique
ni page blanche : elle affiche un message compréhensible, annoncé aux lecteurs d'écran, qui
explique qu'aucun résultat ne peut être produit. Le choix est explicite : plutôt que d'avancer un
résultat partiel, l'application préfère ne rien avancer.


---


## 27. C11 — Monitorer le modèle

`Épreuve E3`

Le monitoring du modèle couvre quatre choses : la dérive des variables, la latence, les erreurs,
et la répartition des verdicts.

La dérive est produite par Evidently, en local, sous forme d'un rapport HTML et d'un JSON
exploitable. Les latences sont mesurées par route, en p50, p95 et maximum, sur une fenêtre
glissante. Deux seuils déclenchent des alertes : un p95 au-dessus de 750 millisecondes, un taux
d'erreur au-dessus de 5 %. Ils ne sont évalués qu'à partir de cinq appels, pour ne pas alerter
sur un échantillon d'un seul point.

Un choix que je veux souligner : **aucune action automatique n'est déclenchée par une alerte**.
Une dérive détectée provoque une revue humaine, jamais un réentraînement automatique. Réentraîner
automatiquement sur des données dérivées, c'est apprendre la dérive.


---


## 28. C12 — Les tests

`Épreuve E3`

Cinquante et un tests, 86 % de couverture. Ils couvrent six familles : les données, le modèle,
la robustesse, l'API, l'application, et la non-régression sur incidents.

Deux points de méthode. Le test du modèle ne se contente pas d'entraîner : il écrit un artefact
temporaire **et le recharge**, parce que c'est le rechargement qui casse en pratique, pas
l'entraînement.

Et sur la non-régression, j'applique une règle systématique : **vérifier dans les deux sens**.
Quand j'écris un test qui doit attraper un bug, je retire le correctif et je confirme que le test
échoue bien. Un test de non-régression qui passe avant la correction ne prouve rien. Cela m'a
servi : j'avais un jour rendu des tests indépendants d'un service externe, et j'ai dû vérifier
que la doublure n'avait pas supprimé leur pouvoir de détection.


---


## 29. C13 — La chaîne de livraison, exécutée

`Épreuve E3` · 📷 **capture : `04-ci-github-verte.png`**

La chaîne de livraison n'est pas un fichier YAML décoratif : elle s'exécute à chaque poussée, sur
Ubuntu, avec Java 17 et un PostgreSQL éphémère.

Elle rejoue **tout** : la génération des fixtures, l'import en base, la collecte, le nettoyage,
et surtout l'entraînement du modèle. Puis les tests, le lint, l'analyse statique de sécurité,
l'audit des dépendances, la porte de conformité, et enfin la construction du paquet.

L'ordre est important : `uv build` est la **dernière** étape. Rien n'est construit si quelque
chose en amont échoue. Et l'artefact publié contient la roue, l'archive source, le modèle gelé,
sa fiche et ses métriques.

Je peux vous donner le lien : cette exécution est publique et consultable.


---


## 30. C13 — La porte de conformité

`Épreuve E3`

C'est la pièce dont je suis le plus satisfait, parce qu'elle transforme « j'ai des tests » en
« j'ai une chaîne qui décide ».

Douze critères sur trois axes — qualité, robustesse, sécurité. Chacun porte son seuil, sa valeur
mesurée, son verdict et **la justification du seuil**. Le tableau est généré, jamais rédigé à la
main. Et le script sort en code non nul si un critère bloquant échoue, ce qui empêche la
construction du paquet.

Un critère mérite une explication : `qualite.chaine_entrainement`. Il **rejoue** l'entraînement
complet, journalisation comprise. Je l'ai ajouté après un incident précis : la porte inspectait
l'artefact — présent, chargeable, contrat conforme — et affichait « conforme » alors que la chaîne
qui produit cet artefact était cassée. Un artefact valide sur le disque ne prouve que le passé.
Il fallait que la porte prouve le présent.


---


## 31. DÉMONSTRATION — le modèle en service

`Épreuve E3` · 📷 **capture : `08-web-resultat-echelles-expliquees.jpg`**

Je passe à la démonstration de l'application. Je vais montrer le parcours d'un particulier, la
bascule vers la lecture analyste, l'accessibilité au clavier, et enfin le comportement quand le
service tombe.

· 5 minutes

> **Fenêtres à préparer avant** : navigateur sur `http://127.0.0.1:3000/`, un terminal visible.

### D1 · Le cas qui refuse de conclure — 1 min 15
**Faire** : accueil → cliquer **« Aucun DPE rapproché »**

> **Dire** : « Je commence par le cas le plus important, et ce n'est pas celui qui donne un
> résultat. Cette mutation n'a aucun diagnostic rapprochable. Le système ne produit pas de score :
> il répond "non évaluable" et affiche "information insuffisante". Il aurait été très facile
> d'imputer une valeur moyenne et de sortir un chiffre. J'ai fait l'inverse. **Refuser de conclure
> quand on ne peut pas est une fonctionnalité, pas un manque** — et c'est le comportement dont un
> analyste a le plus besoin. »

### D2 · La contradiction majeure — 1 min 45
**Faire** : retour accueil → **« Surfaces DVF et DPE incompatibles »**

> **Dire** : « Ici, les trois axes. La cohérence est à 60 % : une contradiction majeure. La surface
> déclarée à la vente et la surface habitable du diagnostic diffèrent de 45 % — ce ne sont
> probablement pas le même logement, mais deux appartements de la même parcelle.
>
> Regardez la combinaison : **cohérence mauvaise, confiance élevée**. Cela signifie "je suis sûr
> qu'il y a un problème". C'est une nuance qui disparaîtrait entièrement si j'avais fusionné les
> trois axes en une note unique.
>
> Et chaque score porte son échelle : "100 % signifie qu'aucune contradiction connue n'a été
> détectée. Ce score ne mesure pas le prix du logement." »

### D3 · La vue analyste — 1 min 15
**Faire** : cliquer **« Voir la version analyste »**

> **Dire** : « Même rapprochement, même calcul — seule la restitution change. Le profil ne modifie
> jamais le résultat : deux utilisateurs qui voient deux chiffres différents sur la même donnée
> serait un défaut de conception.
>
> L'analyste reçoit en plus l'identifiant de la règle déclenchée, `COH-01`, et la décomposition de
> l'écart : quelle variable porte quelle part de l'erreur de reconstruction. C'est la réponse à
> "pourquoi cette ligne est-elle signalée ?". Et la version du modèle qui a produit le verdict. »

### D4 · La preuve de l'appel réel — 45 s
**Faire** : terminal → `curl -i -X POST http://127.0.0.1:8002/predict -H 'Content-Type: application/json' -d '{}'`

> **Dire** : « Et pour prouver que l'application appelle bien une API et n'importe pas le moteur :
> sans clé d'API, la route répond 401. L'application, elle, présente sa propre clé côté serveur —
> elle n'atteint jamais le navigateur. »

---


---


## 32. SECTION — Application

`Épreuve E4`

Troisième bloc : l'application elle-même — son besoin, son architecture, sa sécurité et sa livraison. Il se termine aussi par une démonstration.


---


## 33. C14 — À qui sert cette application

`Épreuve E4`

L'application sert trois publics, et le besoin de chacun est différent.

Le particulier veut comprendre ce que les données permettent de conclure — et surtout ce qu'elles
ne permettent pas. Il reçoit des phrases, pas des chiffres nus. L'analyste crédit veut vérifier
une donnée avant une revue humaine : il reçoit les identifiants de règles, la décomposition de
l'écart et la version du modèle. L'exploitant veut savoir si le service est dégradé.

Et je définis explicitement un hors-périmètre : pas de compte utilisateur, pas de paiement, pas
de décision automatisée sur une personne, pas de saisie d'adresse libre. Ce dernier point est un
choix de minimisation : croiser une adresse précise, un prix et une étiquette énergétique permet
de désigner un logement, donc potentiellement son occupant.


---


## 34. C14 — User stories et critères vérifiables

`Épreuve E4`

Six user stories, chacune avec un critère d'acceptation que je peux vérifier, pas une intention.

Je m'arrête sur deux d'entre elles. La première dit que l'utilisateur veut savoir si un
rapprochement est cohérent **sans** recevoir d'estimation de prix. Le critère est négatif et
vérifiable : aucun champ, aucun texte ne parle de prix prédit. C'est une contrainte que je peux
tester.

La sixième est celle d'un exploitant : il veut pouvoir relier une requête de l'application à
l'appel correspondant dans l'API. Le critère est le même identifiant de corrélation dans les deux
journaux. Je vous montrerai que c'est le cas.


---


## 35. C15 — L'architecture réelle

`Épreuve E4`

Voici l'architecture réelle, pas un schéma générique.

Deux clients, deux APIs, un artefact local, une base PostgreSQL et un service IA local. Le point
que je veux souligner est le chemin de la clé d'API : le navigateur ne parle **jamais** aux ports
Python. Il parle à son propre serveur, qui porte la clé et relaie l'appel.

Cela a deux conséquences. Aucun secret ne se retrouve dans le bundle JavaScript — je l'ai vérifié
en cherchant la clé dans les fichiers compilés, elle n'y est pas. Et il n'y a aucun CORS à
configurer, puisqu'aucune requête n'est inter-origine.

La contrainte qui a le plus structuré l'architecture, c'est le fonctionnement hors ligne. Et je ne
me contente pas de le promettre : un garde-fou intercepte la couche socket et transforme toute
sortie réseau non locale en erreur explicite. Une dépendance oubliée devient une erreur bruyante
au développement, pas une surprise en soutenance.


---


## 36. C15 — Le hors-ligne, prouvé et non promis

`Épreuve E4`

Je reviens sur la contrainte hors ligne, parce que c'est celle qui a le plus structuré
l'architecture, et parce que la manière dont je la traite dit quelque chose de ma méthode.

J'aurais pu me contenter de couper le Wi-Fi le jour de la démonstration. Mais couper le réseau ne
**prouve** rien : cela ne révèle une dépendance cachée qu'au pire moment, devant vous.

J'ai donc installé un verrou au niveau de la couche socket. Toute tentative de connexion vers
autre chose que la boucle locale lève immédiatement une exception nommée, qui indique l'hôte visé.
Une dépendance réseau oubliée devient une erreur bruyante pendant le développement, pas une
surprise en soutenance.

Et ce verrou est lui-même couvert par un test : le test désactive le garde-fou, démarre
l'application, vérifie que le démarrage l'a bien réarmé, puis vérifie qu'une résolution DNS
externe échoue. Si quelqu'un retire cette protection, le test tombe.


---


## 37. C16 — Le pilotage, et sa limite assumée

`Épreuve E4`

Sur la coordination, je vais être direct, parce que c'est une limite et que je préfère l'annoncer
moi-même.

Le référentiel attend une conduite agile avec des rôles, des rituels et une animation collective.
Je réalise ce projet seul. Je ne simule donc aucune équipe : ce serait la première chose qu'une
question ferait tomber.

Ce que je montre est réel : un kanban, un backlog, un journal de décisions daté où chaque choix
structurant est consigné avec l'alternative écartée et la raison, une définition de « terminé »,
et une rétrospective. La couverture collective de C16 est donc partielle, et je l'assume.

En revanche, l'énoncé de C16 mentionne aussi un **contexte MLOps**, et cette moitié-là est
entièrement couverte : chaîne exécutée, artefact versionné, porte de conformité, incidents tracés.


---


## 38. C16 — À quoi ressemble une décision tracée

`Épreuve E4`

Je veux montrer concrètement à quoi ressemble une décision tracée, parce que « journal de
décisions » peut vouloir dire n'importe quoi.

Chaque entrée porte trois choses : la décision, l'alternative que j'ai écartée, et la raison. La
deuxième est la plus importante — c'est elle qui distingue un journal d'une liste de choses faites.

Trois exemples. Le garde-fou hors ligne : j'ai écarté l'option évidente, couper le Wi-Fi le jour J,
parce qu'elle ne prouve rien et ne révèle une dépendance cachée qu'au pire moment.

Le choix du framework applicatif : j'ai écarté Streamlit, qui aurait été bien plus rapide, parce
que son DOM est généré et que je n'aurais pas pu garantir l'accessibilité que C14 et C17 exigent.

Et le plus récent : faire lire les APIs par des composants serveur plutôt que par le navigateur.
L'alternative — une clé publique dans le bundle — aurait fonctionné, et aurait fait fuiter le
secret.

À chaque fois, ce que je consigne n'est pas ce que j'ai fait : c'est **pourquoi je n'ai pas fait
l'autre chose.** C'est ce qui rend une décision défendable six mois plus tard.


---


## 39. C17 — Accessibilité, mesurée et non déclarée

`Épreuve E4`

L'accessibilité, maintenant, et je voudrais montrer la différence entre l'annoncer et la mesurer.

La structure est sémantique, le premier élément focusable est un lien d'évitement, le résultat
est annoncé aux lecteurs d'écran par une région `aria-live`, les erreurs par `role="alert"`.

Mais le point sur lequel j'insiste, c'est le contraste. Je n'ai pas estimé « ça a l'air lisible » :
j'ai calculé les ratios de luminance de chaque couple couleur-fond de ma palette, dans les deux
thèmes. En thème clair, le plus serré est à 4,53 pour un seuil AA à 4,5. En thème sombre, le plus
serré est à 6,01. Tout passe, et je peux vous montrer le calcul.

Enfin, le sens n'est jamais porté par la seule couleur : un état « à vérifier » porte le mot « à
vérifier », pas seulement une teinte orange. C'est le critère qui bénéficie le plus aux
daltoniens, et c'est le plus souvent oublié.


---


## 40. C17 — Sécurité applicative

`Épreuve E4`

Sur la sécurité, quatre mécanismes, chacun rattaché à un risque OWASP identifié.

Les en-têtes de durcissement, posés sur toutes les réponses. La politique de sécurité du contenu
interdit toute ressource distante — ce qui est aussi ma contrainte hors ligne, les deux se
renforcent.

La comparaison des clés se fait à **temps constant**. Une comparaison naïve s'arrête au premier
caractère différent, et la durée de réponse fuit alors la clé, caractère par caractère. C'est une
attaque réelle, et la parade tient en une fonction.

Les journaux pseudonymisent les champs personnels **avant** l'écriture sur disque, pour qu'un
fichier de log ne devienne pas une base de données personnelles clandestine.

Et le dernier, dont je suis satisfait : `import "server-only"` en tête du module qui porte la clé
d'API. Ce n'est pas une convention, c'est une garantie mécanique : si un développeur importe ce
module depuis un composant client, **le build échoue**. Il est impossible de faire fuiter la clé
par inadvertance.


---


## 41. C17 — Intégrer un service d'IA sans lui donner autorité

`Épreuve E4`

L'épreuve porte sur une application intégrant un service d'intelligence artificielle. Voici
comment je l'ai intégré, et surtout où j'ai mis la frontière.

Le service local reformule en langage courant une explication **déjà calculée**. Il reçoit une
**instruction de rédaction** choisie par le code en fonction du verdict — pas le verdict à
interpréter. Il ne voit jamais les données brutes, ne produit aucun score, ne modifie aucun
chiffre.

Cette frontière n'est pas théorique, et je peux vous dire précisément pourquoi je l'ai posée là.
En expérimentant, j'ai donné au modèle un verdict à reformuler : cohérence 60 %, contradiction
majeure. Il a répondu que « le rapprochement est jugé cohérent malgré cette anomalie ». **Il avait
inversé le sens.**

C'est la démonstration expérimentale du principe que le projet applique partout : le composant qui
explique n'a pas autorité sur ce qu'il explique. Les scores et les motifs restent affichés à côté
du texte reformulé, donc toute divergence est visible immédiatement.

Enfin, la route est isolée de `/predict`, avec un délai de trois secondes et un repli garanti sur
le texte assemblé. La prédiction n'est jamais ralentie ni mise en danger par le service IA.


---


## 42. C18 — Les tests automatisés au versionnement

`Épreuve E4`

L'intégration continue se déclenche à chaque poussée et enchaîne dix-sept étapes.

Au-delà des tests et du lint, j'ai branché deux contrôles de sécurité. Bandit, qui fait l'analyse
statique du code Python et cherche les motifs dangereux. Et pip-audit, qui compare mon graphe de
dépendances à une base d'avis de sécurité publiés.

Ce second contrôle correspond exactement à l'entrée A06 de l'OWASP Top 10 : composants vulnérables
et obsolètes. Et il a servi : il a détecté deux vulnérabilités réelles dans mes dépendances, dont
une corrigeable. J'y reviens dans la dernière épreuve, parce que c'est devenu un incident documenté.

Le point important : la sécurité n'est pas une relecture ponctuelle, c'est une vérification
automatique à chaque commit.


---


## 43. C19 — La livraison, conditionnelle

`Épreuve E4`

La livraison, enfin. Le processus produit un paquet Python et une image Docker, tous deux
disponibles localement — l'image est déjà construite, la démonstration ne télécharge rien.

Mais l'élément que je veux souligner, c'est la position de la porte de conformité : **avant** la
construction. Douze critères de qualité, robustesse et sécurité sont évalués, et si un seul
critère bloquant échoue, le script sort en code non nul et rien n'est construit.

C'est ce qui fait la différence entre une chaîne qui teste et une chaîne qui **décide**. La
livraison est conditionnelle : elle n'a lieu que si le système se déclare conforme, et ce verdict
est calculé, pas rédigé.


---


## 44. DÉMONSTRATION — l'application

`Épreuve E4` · 📷 **capture : `07-web-accueil-le-pourquoi-et-glossaire.jpg`**

Je passe à la démonstration de l'application. Je vais montrer le parcours d'un particulier, la
bascule vers la lecture analyste, l'accessibilité au clavier, et enfin le comportement quand le
service tombe.

· 5 minutes

### D1 · Le parcours et sa lisibilité — 1 min 30
**Faire** : `http://127.0.0.1:3000/` — rester sur l'accueil, faire défiler lentement

> **Dire** : « La première chose que voit l'utilisateur n'est pas un formulaire, c'est le problème :
> deux bases publiques décrivent le même logement sans identifiant commun, le rapprochement peut
> être faux, et rien ne le signale.
>
> Juste en dessous, le vocabulaire est défini — DVF+, DPE, rapprochement — parce qu'aucune
> connaissance préalable n'est attendue de l'utilisateur. Et l'avertissement est permanent :
> Concorde n'estime aucun prix.
>
> Les cinq cas proposés sont extraits de la table réelle. Vous voyez les noms de communes, les
> étiquettes énergétiques sur leur échelle, les dates en clair — pas des identifiants de base de
> données. »

### D2 · Les trois axes et l'échelle — 1 min 15
**Faire** : cliquer **« Surfaces DVF et DPE incompatibles »**

> **Dire** : « Les trois axes, et chacun porte son échelle. "100 % signifie qu'aucune contradiction
> connue n'a été détectée. Ce score ne mesure pas le prix du logement." Un pourcentage nu ne veut
> rien dire ; celui-ci est accompagné de sa lecture.
>
> Et la section "Pourquoi ce résultat ?" donne le motif en français, avec sa gravité — pas un code
> d'erreur. »

### D3 · L'accessibilité, au clavier — 1 min
**Faire** : recharger, puis **Tab** une fois → le lien d'évitement apparaît ; **Tab** plusieurs fois

> **Dire** : « L'accessibilité se démontre, elle ne se déclare pas. Je recharge, j'appuie une fois
> sur Tab : le premier élément focusable est le lien d'évitement, qui permet d'atteindre le contenu
> sans traverser la navigation. Il est invisible jusqu'au focus clavier.
>
> Je continue : chaque élément reçoit un contour de focus visible et contrasté. Tout le parcours se
> fait sans souris. »

### D4 · Ce qui se passe quand ça casse — 1 min 15
**Faire** : terminal → `pkill -f "uvicorn api.model.main"` → recharger la page de résultat

> **Dire** : « Et voici le cas qui compte le plus. J'arrête l'API du modèle et je recharge.
>
> L'application n'affiche ni page blanche, ni trace technique, ni erreur 500. Elle affiche
> "Résultat indisponible", avec un message compréhensible, annoncé aux lecteurs d'écran par
> `role="alert"`. Aucun résultat partiel n'est présenté : **en cas de panne, l'application préfère
> ne rien avancer plutôt qu'avancer quelque chose d'invalide.**
>
> C'est un comportement conçu et couvert par un test, pas un heureux hasard. »

**Faire** : relancer l'API pour la suite
```bash
.venv/bin/uvicorn api.model.main:app --host 127.0.0.1 --port 8002 &
```

---


---


## 45. SECTION — Service d'IA

`Épreuve E2`

Quatrième bloc : le service d'intelligence artificielle. Vous venez de le voir tourner ; je reviens sur la façon dont je l'ai choisi et configuré.


---


## 46. Le chemin que je vais suivre

`Épreuve E2`

Cette épreuve porte sur le service d'intelligence artificielle : comment je l'ai choisi, installé
et configuré.

Elle arrive après les deux démonstrations, ce qui me va bien : vous avez déjà vu le service
tourner dans l'application. Je ne vais donc pas défendre un choix théorique, je vais expliquer
comment j'y suis arrivé, et surtout ce que j'ai mesuré avant de lui faire confiance.

Je suivrai le chemin complet : le besoin reformulé, la veille qui l'encadre, les alternatives
comparées, le choix, le paramétrage, et les limites que j'ai constatées.


---


## 47. C7 — Le besoin reformulé

`Épreuve E2`

Le besoin d'abord, parce que c'est lui qui commande le reste.

Le verdict que produit Concorde est exact, mais il est rédigé par assemblage de conditions : « une
contradiction majeure détectée, cohérence 60 %, les données permettent de le dire avec un bon
niveau de certitude ». C'est juste, mais c'est écrit par une machine, et un particulier lit mieux
une phrase.

Le besoin est donc précis : reformuler en français courant un verdict **déjà calculé**. J'insiste
sur « déjà calculé », parce que c'est ce qui définit la frontière.

En entrée, le service reçoit uniquement le verdict : niveaux, scores, nombre de motifs. Jamais
les données brutes, jamais une adresse, jamais une parcelle. En sortie, il produit une phrase et
rien d'autre : aucun score, aucun chiffre, aucun jugement.

Et le critère de réussite est explicite : la phrase doit être lisible, conforme au verdict,
produite en moins de trois secondes, et son échec ne doit jamais dégrader le service.


---


## 48. C6 — La veille, et sa qualification

`Épreuve E2`

La veille, maintenant. Le coaching est explicite sur ce point : accumuler des liens sans expliquer
leur fiabilité ne prouve pas la compétence.

J'ai donc deux choses. D'abord un outil d'agrégation réellement configuré : un fichier OPML
importable dans un lecteur RSS local, qui contient les flux officiels de l'ADEME, de la CNIL, de
PyPI et des dépôts GitHub de mes dépendances critiques.

Ensuite une grille de qualification. Chaque source est évaluée sur six critères : qui publie, la
date, s'il s'agit d'une source primaire, si l'information converge avec d'autres, si elle est
accessible, et quel est son biais.

Ce dernier critère est celui que je trouve le plus utile. L'ADEME est une source primaire
excellente, mais sa base DPE n'est pas un échantillon représentatif du parc français — l'agence le
dit elle-même. C'est ce biais identifié qui m'a conduit à afficher des réserves partout dans
l'application plutôt qu'à présenter un DPE comme une vérité.

Un point d'honnêteté : data.gouv.fr et Géorisques ne publient pas de flux RSS stable pour les jeux
que je suis. J'ai testé les URL candidates, elles répondent 404. Je les conserve comme pages de
consultation manuelle, et je ne les présente pas comme des flux. C'était plus simple d'invoquer un
service d'agrégation en ligne que je n'ai pas configuré — je préfère une limite visible.


---


## 49. C6 — Le rythme et ce qu'il déclenche

`Épreuve E2`

Sur le rythme : revue quotidienne jusqu'à la soutenance, puis hebdomadaire.

Ce que je veux souligner, c'est ce qu'une alerte déclenche. Elle n'est pas simplement lue : si
elle touche le contrat, la sécurité, une source ou une dépendance, elle produit une entrée datée
dans mon journal de décisions, une preuve adaptée, et si nécessaire un incident documenté.

Le principe que je m'impose : une source ne devient jamais une exigence automatique. Elle est
interprétée dans le périmètre du projet, et la décision qui en découle est tracée avec sa raison.

Et je dois annoncer une limite. Le référentiel attend une veille qui **anime un travail collectif**
— sélection des sources, partage des synthèses aux parties prenantes. Je suis seul. Je ne simule
aucune équipe : la compétence est donc partiellement couverte, et je préfère vous le dire
plutôt que vous laisser le découvrir.


---


## 50. C7 — La matrice de comparaison

`Épreuve E2`

La matrice de comparaison, sur quatre axes : l'adéquation fonctionnelle, la faisabilité technique,
le risque, et la décision.

LM Studio avec Gemma 4B est retenu, mais notez la formule : **retenu sous garde-fou**. J'y reviens
dans deux slides, parce que le risque que j'ai mesuré est réel.

Ollama est écarté non pas pour une faiblesse fonctionnelle — il ferait la même chose — mais parce
qu'il n'est pas installé et qu'aucun modèle n'y est chargé. Le télécharger ajouterait du temps,
du stockage et une dépendance de démonstration, pour zéro valeur supplémentaire.

Les API cloud sont écartées frontalement : elles contredisent mes contraintes. Elles exigent un
réseau, transfèrent mes prompts à un tiers, coûtent de façon variable, et sont indisponibles hors
ligne.

Et le dernier est intéressant : mon propre auto-encodeur. Il est déjà là et il est excellent pour
ce qu'il fait. Je l'écarte quand même pour la reformulation, parce que le détourner en générateur
de texte confondrait le calcul du verdict et sa restitution. Ces deux responsabilités doivent
rester séparées.


---


## 51. C8 — Installation et paramétrage

`Épreuve E2`

L'installation et le paramétrage. Le service est LM Studio, qui expose une API compatible OpenAI
sur la boucle locale. Le modèle, Gemma 4B en quatre bits, est déjà présent sur le disque : rien
n'est téléchargé au moment de la démonstration.

Cinq paramètres, chacun justifié. La température à zéro, pour la reproductibilité : la même
consigne doit produire la même phrase. Quatre-vingt-dix tokens, parce qu'une phrase suffit et que
ça borne à la fois le coût et la latence. Un délai HTTP de trois secondes, au-delà duquel le
repli vaut mieux que l'attente.

La liaison à `127.0.0.1` est un choix de sécurité : seul l'utilisateur de la machine peut
atteindre le service, et aucune donnée Concorde ne quitte le poste.

Et le TTL d'une heure : je l'ai ajouté après une mesure. Le modèle se décharge après inactivité,
et le premier appel suivant prend dix-huit secondes de repagination. En le maintenant résident, on
passe à moins d'une seconde.


---


## 52. C8 — Ce que j'ai mesuré avant de faire confiance

`Épreuve E2`

Voici la partie dont je suis le plus satisfait, parce qu'elle explique pourquoi le service est
« retenu **sous garde-fou** ».

Première mesure : j'ai cru que le modèle était lent. En répétant la même requête triviale, j'ai
obtenu dix-huit secondes, puis huit, puis un tiers de seconde. Ce n'était pas le modèle, c'était
sa repagination en mémoire. D'où le TTL.

Deuxième mesure : Gemma 4 sur moteur MLX déclenche un mode raisonnement qui consomme tout le
budget de tokens et laisse la réponse vide. J'ai testé quatre paramètres pour le désactiver.
Aucun ne fonctionne proprement — c'est un bug amont documenté, que je cite dans ma veille.

Troisième mesure, et c'est la découverte utile : c'est la **forme de la consigne** qui décide.
Demandez au modèle de « reformuler ce verdict », il analyse, consomme 551 tokens de raisonnement
et met trente et une secondes. Demandez-lui d'« écrire une phrase disant que X », il rédige, en un
demi-seconde, sans raisonner.

Et la quatrième mesure est celle qui a fixé l'architecture. Quand je lui ai donné un verdict à
interpréter avec un budget suffisant, il a répondu que « le rapprochement est jugé cohérent » —
alors que le verdict transmis était une cohérence de 60 % avec une contradiction majeure. **Il
avait inversé le sens.**


---


## 53. C8 — La conception qui en découle

`Épreuve E2`

De ces mesures découle toute la conception.

Le code choisit la consigne en fonction du verdict déjà calculé. Le modèle ne reçoit qu'une
**instruction de rédaction** : il ne peut pas inverser un sens qu'on ne lui demande pas d'établir.
C'est la parade directe à la quatrième mesure.

Cinq conditions déclenchent le repli : délai dépassé, sortie vide ou trop courte, arrêt anormal,
présence de tokens de raisonnement, ou erreur HTTP. Dans tous ces cas, l'utilisateur reçoit le
texte assemblé, et la réponse indique sa provenance.

Le taux de repli est mesuré et exposé dans les métriques. Ce n'est pas un aveu de faiblesse :
c'est un instrument. Un service dont on chiffre la fiabilité vaut mieux qu'un service dont on
affirme qu'il marche.

Enfin, deux précautions. La sortie du modèle est traitée comme du contenu **non fiable** : bornée,
échappée, jamais rendue comme du HTML. Et les scores et les motifs restent affichés à côté du
texte, inchangés — si le modèle dérive, l'écart se voit immédiatement.


---


## 54. C8 — Le service est surveillé, pas seulement branché

`Épreuve E2`

Dernier volet de C8 : le monitorage du service, parce que l'installer ne suffit pas.

Avant tout appel, un contrôle vérifie non pas qu'un serveur répond, mais que **le modèle exact
attendu** est exposé. C'est une distinction qui compte : LM Studio peut très bien tourner avec un
autre modèle chargé, et mes consignes sont calibrées pour celui-ci. Un serveur qui répond n'est
pas une garantie.

Chaque vérification écrit un événement dans les journaux structurés, et un fichier de métriques
qui accumule les appels, les erreurs, la latence et le taux de repli.

Ce taux de repli est l'indicateur que je regarde. Il ne cache pas la fragilité du modèle, il la
chiffre. Et c'est ce qui me permet de dire aujourd'hui « deux réponses acceptées sur trois en
mesure à chaud » plutôt que « ça marche généralement ».

Enfin, en cas d'absence du serveur ou du modèle, l'erreur est explicite et nommée. Il n'y a jamais
d'appel silencieux vers le vide, ni de résultat vaguement dégradé sans que personne ne le sache.


---


## 55. SECTION — Exploitation

`Épreuve E5`

Dernier bloc : l'exploitation. Le monitorage applicatif, et la résolution d'incident.


---


## 56. C20 — Ce que je journalise, et ce que je refuse de journaliser

`Épreuve E5`

Le monitorage applicatif, et je commence par ce que je refuse de journaliser.

Les journaux sont au format JSON Lines : une ligne JSON par événement, exploitable directement
avec `jq`, sans parser du texte libre et fragile.

Mais le point important est le filtre de pseudonymisation. Les champs identifiés comme personnels
— adresse, nom, email, adresse IP, clé d'API — sont remplacés par une empreinte SHA-256 tronquée
**avant** l'écriture sur disque. Pas après, pas à la lecture : avant.

La raison est directe. On protège soigneusement une base de données, et on laisse les mêmes
informations s'accumuler en clair dans les journaux pendant des mois. Un fichier de log ne doit
jamais devenir une base de données personnelles clandestine. L'empreinte permet quand même de
compter, de corréler et de dédupliquer, sans stocker la donnée elle-même.


---


## 57. C20 — La corrélation de bout en bout

`Épreuve E5`

Deuxième brique : la corrélation.

Chaque requête reçoit un identifiant, propagé par une variable de contexte à travers
l'application, l'appel HTTP à l'API, et la prédiction. Le même identifiant apparaît donc dans les
journaux des deux services.

La conséquence pratique est celle-là : quand un utilisateur signale un comportement anormal, je
n'ai pas à recouper des horodatages entre deux fichiers. Je filtre sur un identifiant et j'obtiens
la trace complète de sa requête, de son clic jusqu'au verdict.

C'est ce qui transforme un incident en quelque chose de rejouable plutôt qu'en enquête.


---


## 58. C20 — Seuils, alertes, tableau de bord

`Épreuve E5` · 📷 **capture : `04-surveillance-locale-seuils-alertes.jpg`**

Troisième brique : les seuils et les alertes.

Pour chaque route, je mesure les appels, les erreurs client, les erreurs serveur, et les latences
en p50, p95 et maximum sur une fenêtre glissante.

Deux seuils déclenchent des alertes : un p95 au-dessus de 750 millisecondes en avertissement, un
taux d'erreur au-dessus de 5 % en critique. Et une précaution qui compte : ils ne sont évalués
qu'à partir de cinq appels sur une même route. Alerter sur un échantillon d'un seul point produit
du bruit, et une alerte qui crie pour rien finit par être ignorée.

Le tout est restitué sur une page locale. Aucune métrique n'est envoyée à un service externe :
c'est cohérent avec la contrainte hors ligne et avec le registre RGPD.


---


## 59. C21 — Cinq incidents réels

`Épreuve E5`

Sur la résolution d'incident, je n'ai pas eu à en provoquer un : le projet m'en a fourni cinq,
tous réels, tous documentés.

Le premier vient de l'intégration continue : un ordre d'initialisation erroné, puis un défaut de
packaging. Le deuxième cassait ma propre démonstration : un clic sur le sélecteur de profil
renvoyait une erreur 405 en JSON brut. Le troisième est le plus instructif sur la méthode. Le
quatrième vient de la porte de conformité, qui a détecté deux vulnérabilités réelles dans mes
dépendances. Et le cinquième porte sur l'outil de contrôle lui-même.

Chacun suit la même discipline : reproduction, diagnostic, correctif minimal, test de
non-régression vérifié **dans les deux sens**, et retour d'expérience.

Je vais en détailler deux.


---


## 60. C21 — L'incident qui cassait la démonstration

`Épreuve E5` · 📷 **capture : `06-bascule-profil-corrigee.jpg`**

Le premier que je détaille est celui qui cassait ma propre démonstration.

Depuis la page de résultat, cliquer sur « Analyste crédit » affichait un JSON brut : « Method Not
Allowed ». En plein milieu du parcours, sur l'étape censée être la plus convaincante — le même
rapprochement, deux lectures.

Le diagnostic est intéressant parce que la cause n'était pas où on la cherche. Les liens du
bandeau étaient relatifs. Un lien relatif conserve le chemin courant et émet un GET. Sur mes trois
pages en GET, il fonctionnait parfaitement. Sur la page de résultat, déclarée en POST parce
qu'elle répondait à un formulaire, il n'y avait aucun gestionnaire.

Le défaut n'était donc ni dans le modèle ni dans l'API : c'était une **hypothèse implicite du
gabarit** — « toute page est atteignable en GET » — vraie pour trois pages sur quatre.

Correctif en deux temps : un gestionnaire GET qui partage la même fonction de rendu, et des liens
construits côté serveur. Six tests de non-régression, et je les ai vérifiés dans les deux sens :
j'ai retiré le correctif pour confirmer qu'ils échouaient bien, avec le 405 dans le journal.


---


## 61. C21 — Quand le poste ment

`Épreuve E5`

Un troisième, très court, parce que sa leçon est différente des deux autres.

Six tests que je venais d'écrire passaient sur ma machine et échouaient en intégration continue.
Le symptôme était instructif : ils échouaient en 503, pas en 405. Ce n'était donc pas le bug
d'origine qui réapparaissait.

Le 503 est le code que mon application renvoie quand elle ne joint pas l'API modèle. Or mes tests
instanciaient l'application, qui appelle son amont en HTTP. Cette API tourne en permanence sur mon
poste, et jamais sur un runner GitHub. Mes tests exigeaient donc silencieusement un service
démarré — exactement le défaut qu'ils étaient censés empêcher chez les autres.

J'ai remplacé le transport par une doublure, en conservant le vrai moteur. Et j'ai ensuite vérifié
que cette doublure ne les avait pas rendus aveugles, en retirant le correctif du 405 : les six
échouent bien.

La règle que j'en tire : **un test qui réussit en local et échoue en CI ne signale pas un problème
de CI. Il signale que le poste fournissait silencieusement quelque chose.**


---


## 62. C21 — Quand l'outil de contrôle se trompe

`Épreuve E5`

Le second est le plus intéressant, parce qu'il porte sur mon outil de contrôle lui-même.

Pour corriger une vulnérabilité, j'avais changé de distribution MLflow. Le raisonnement était
juste, mais la nouvelle distribution n'embarquait pas une dépendance du magasin de suivi. La
chaîne d'entraînement ne fonctionnait plus.

Ce qui rend cet incident instructif, c'est que **trois filets de sécurité l'ont laissé passer**.
Le test neutralisait la journalisation, donc le chemin cassé n'était jamais exercé. La porte de
conformité vérifiait que l'artefact existait, se chargeait et respectait son contrat — et les
trois étaient vrais, parce qu'un artefact valide était resté sur le disque depuis le passage
précédent. Et ma documentation affirmait explicitement le contraire de la réalité.

La leçon tient en une phrase : **un artefact valide ne prouve que le passé.** Un contrôle qui
inspecte un résultat ne prouve pas que le processus qui l'a produit fonctionne encore.

J'ai donc ajouté un critère bloquant qui **rejoue** l'entraînement complet, dans un répertoire
temporaire pour ne pas altérer l'artefact suivi. Vérifié dans les deux sens : dépendance retirée,
la porte passe à non conforme et sort en code 1 ; dépendance remise, elle repasse au vert.


---


## 63. Le motif récurrent

`Épreuve E5`

En reprenant mes cinq incidents, un motif est apparu, et c'est ce que j'emporte de ce projet.

Quatre sur cinq avaient la même cause profonde : **la documentation affirmait ce que le code ne
faisait pas.** Mon registre RGPD annonçait une minimisation que l'API ne respectait plus. Mon
`.gitignore` affirmait un versionnement DVC qui n'existait pas. Ma documentation de sécurité
affirmait un suivi MLflow qui était cassé.

À chaque fois, la correction a consisté à faire deux choses, pas une : rendre l'affirmation
vraie, **et** la faire vérifier automatiquement par un test ou un critère de conformité.

C'est la raison pour laquelle mon registre RGPD est aujourd'hui protégé par un test, et pourquoi
ma porte de conformité rejoue la chaîne au lieu d'inspecter son résultat.

Une preuve qui n'est pas exécutée n'est pas une preuve. C'est ce que ce projet m'a appris, et
c'est ce que je retiens au-delà de la certification.

Je vous remercie, je suis à votre disposition pour vos questions.


---


## 64. Bilan

`Épreuve E5`

Pour conclure : dix-neuf compétences prouvées, deux partiellement couvertes et assumées
comme telles, aucune laissée de côté. Cinquante et un tests, quatre-vingt-six pour cent de
couverture, douze critères de conformité bloquants et cinq incidents réels documentés.

Les limites, je les redis parce qu'elles font partie du travail : les métriques de règles sont
circulaires sur mon jeu de démonstration, la base DPE n'est pas représentative du parc français,
le rapprochement par parcelle reste ambigu en copropriété, et je ne prédis aucun prix.

Ce que j'emporte de ce projet tient en une phrase : **une preuve qui n'est pas exécutée n'est pas
une preuve.** C'est ce qui m'a fait écrire un test pour mon registre RGPD, et faire rejouer la
chaîne à ma porte de conformité au lieu de lui faire inspecter un résultat.

Je vous remercie, je suis à votre disposition pour vos questions.


---
