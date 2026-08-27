# Questions probables du jury — réponses courtes

Fiche à garder ouverte pendant la soutenance. Chaque réponse tient en deux à quatre
phrases : **on répond, on donne la preuve, on s'arrête.** Ne pas dérouler tout ce qu'on
sait — le jury relance s'il veut plus.

Règle générale : si on ne sait pas, on le dit et on dit ce qu'on ferait pour le savoir.
C'est mieux noté qu'une réponse floue.

---

## A. Les questions les plus probables

### 1. « Pourquoi ce n'est pas déployé en ligne ? »
C'est la plus probable. D'autres candidats sont sur Vercel ou Render avec des URL publiques.

> Le hors-ligne strict est une contrainte que je me suis imposée, pas une limite que j'ai subie.
> Une démonstration qui dépend du réseau d'une salle d'examen n'est pas une démonstration.
> Et je ne me suis pas contenté de couper le Wi-Fi : un garde-fou au niveau des sockets lève
> une exception sur toute connexion sortante non locale, donc la propriété est **testée**,
> pas promise. Le déploiement, lui, est prouvé autrement : l'image Docker est construite et
> la porte de conformité s'exécute avant la construction du paquet.

### 2. « Vous n'avez que 54 tests. »
> Cinquante-quatre tests, 86 % de couverture — et surtout, chacun a été vérifié dans les deux
> sens : j'ai retiré le correctif et confirmé que le test échoue. Un test qui n'a jamais été
> vu rouge ne prouve rien. J'ai justement eu deux cas de tests verts par accident
> d'environnement, que cette discipline a permis de trouver.

### 3. « Vous avez utilisé des assistants IA. Qu'avez-vous fait vous-même ? »
Question délicate et probable. Ne pas se justifier, ne pas minimiser.

> J'ai travaillé avec Claude Code et Codex, et c'est documenté dans mon journal de décisions.
> Ce que j'ai fait moi-même, c'est le cadrage, les décisions d'architecture, et surtout la
> vérification : je n'ai rien accepté sur déclaration. Quand un agent m'a annoncé que tout
> était terminé, j'ai vérifié et trouvé six tests en échec et zéro capture. C'est cette
> méthode-là que je défends aujourd'hui, et elle est visible dans le projet : c'est exactement
> pour ça que j'ai écrit une porte de conformité qui rejoue la chaîne au lieu d'inspecter un
> résultat.

### 4. « Pourquoi ne prédisez-vous pas de prix ? C'est la question intéressante. »
> Parce qu'un modèle de risque ne vaut jamais mieux que ses entrées, et que personne ne
> vérifie les entrées. Et parce qu'estimer une valeur ou une solvabilité ferait entrer le
> projet dans le champ haut risque du règlement européen sur l'IA, avec les obligations qui
> vont avec. Le prix est présent dans mes données, mais il me sert de **signal de cohérence**,
> jamais de cible.

### 5. « Vos métriques sont circulaires, vous le dites vous-même. Alors elles ne valent rien ? »
> Elles ne valent rien comme mesure de performance, et c'est pour ça que je le dis avant qu'on
> me le demande. Ce qu'elles mesurent, c'est que la chaîne fonctionne de bout en bout.
> La seule métrique que je défends comme informative est l'AUC de l'auto-encodeur, à 0,91,
> parce qu'il n'a jamais vu les règles. Une validation honnête demanderait un jeu annoté par
> un tiers, que je n'ai pas.

### 6. « Et si le modèle tombe ? »
Ouvrir `reports/captures/19-jinja-degradation-evaluation-impossible.jpg`.

> Les deux clients refusent de conclure. Aucun résultat partiel n'est affiché : l'application
> préfère ne rien avancer plutôt qu'avancer quelque chose d'invalide. C'est un choix, pas un
> défaut — un score affiché sans son modèle serait pire qu'une absence de score.

---

## B. Sur les données (C1–C5)

### 7. « Pourquoi Spark sur 726 lignes ? C'est disproportionné. »
> Parce que la cible n'est pas ma fixture, c'est la base ADEME : plus de dix millions de DPE.
> J'écris la chaîne avec l'outil de la cible, pas celui du prototype. Le coût, c'est la
> contrainte du JDK 17 — Spark 3.5 refuse le JDK 26 du poste. Elle est fixée dans un script
> et dans la configuration des tests, pas laissée au hasard de la machine.

### 8. « 922 rapprochements, c'est très peu. Ça passe à l'échelle ? »
> Le volume est celui d'une fixture de démonstration, versionnée pour être reproductible.
> Ce qui passe à l'échelle, c'est la chaîne : Spark pour la lecture, PostgreSQL indexé pour
> le stockage, des règles qui s'appliquent ligne à ligne. Ce qui ne passerait pas en l'état,
> c'est le rapprochement par parcelle, qui est un produit cartésien local — il faudrait le
> partitionner par commune.

### 9. « Vous n'avez aucune donnée personnelle. Pourquoi un registre RGPD ? »
> Parce que je manipule des adresses, et qu'une adresse de logement associée à une transaction
> est une donnée indirectement identifiante. J'ai donc pseudonymisé en SHA-256 **avant**
> l'écriture sur disque, et minimisé : aucune adresse détaillée n'est publiée par l'API.
> Et cet engagement n'est pas déclaratif — un test marqué `regression` interroge les trois
> routes exposées et échoue si une adresse réapparaît.

### 10. « Comment ajoutez-vous une nouvelle source ? »
> Une classe qui hérite du contrat `Collecteur` et implémente une seule méthode. Le socle
> mutualise le point d'entrée, la journalisation, la gestion d'erreur, l'écriture et le
> manifeste. Une nouvelle source coûte une vingtaine de lignes et hérite de toutes les
> garanties, dont celle qu'une source en panne n'arrête pas les autres.

---

## C. Sur le modèle (C9–C13)

### 11. « Pourquoi un auto-encodeur et pas une classification ? »
> Parce qu'il n'existe aucune étiquette « ce rapprochement est faux » dans les données
> publiques. Personne n'a annoté les appariements. Le problème est non supervisé par nature.
> L'auto-encodeur apprend à reconstruire la structure normale ; ce qu'il reconstruit mal est
> atypique.

### 12. « Comment fixez-vous le seuil d'anomalie ? »
> Par percentile sur le jeu d'entraînement, pas par une valeur absolue choisie à la main.
> Le seuil et la grille de calibration sont gelés dans l'artefact, avec la graine aléatoire,
> l'empreinte du jeu d'entraînement et le commit Git — donc le résultat est rejouable.

### 13. « D'où viennent vos cinq seuils de règles ? »
> Chacun a une justification métier écrite dans le code, pas un chiffre choisi pour que ça
> marche. Vingt pour cent d'écart de surface, parce que la surface bâtie DVF et la surface
> habitable DPE ne mesurent pas la même chose et qu'un écart modéré est attendu. Dix ans,
> parce que c'est la durée de validité réglementaire d'un DPE. Ils sont affichés dans
> l'application, servis par l'API, jamais recopiés dans l'interface.

### 14. « Pourquoi trois axes séparés plutôt qu'un score global ? »
> Parce qu'une moyenne détruirait l'information. Mon cas de démonstration est à 60 % de
> cohérence avec une contradiction majeure, et une confiance élevée — les données sont
> fiables, et c'est précisément pour ça que je peux affirmer la contradiction. Un score
> unique effacerait cette nuance, qui est toute la valeur du système.

### 15. « Que fait votre 206 ? »
> Ce sont les rapprochements sans DPE. Je les conserve et je ne les score jamais. Il aurait
> été plus flatteur de les écarter, le taux de traitement aurait été meilleur. L'absence
> d'information est une information.

---

## D. Sur le service d'IA (C6–C8)

### 16. « Si le code décide tout, à quoi sert le LLM ? »
> À formuler, et à rien d'autre. Le code choisit l'instruction, le modèle la met en français.
> Cette frontière n'est pas théorique : je l'ai posée **après** l'avoir mesurée. Sur un cas
> à 60 % de cohérence portant une contradiction majeure, le modèle a écrit « jugé cohérent ».
> Il a inversé le verdict. Depuis, il n'a aucune autorité sur la conclusion, un délai de
> trois secondes, quatre-vingt-dix jetons, et un repli local s'il ne répond pas.

### 17. « Pourquoi un modèle local plutôt qu'une API ? »
> Contrainte hors ligne d'abord. Ensuite parce qu'aucune donnée ne sort du poste, ce qui
> règle la question du transfert. Le coût, c'est le démarrage à froid : 18,9 secondes la
> première fois, 0,34 ensuite — donc le modèle est préchargé avant la démonstration.

---

## E. Sur l'application et l'exploitation (C14–C21)

### 18. « Comment garantissez-vous que la clé d'API n'atteint pas le navigateur ? »
> Par construction : le navigateur ne parle jamais aux ports 8001 et 8002. Les appels partent
> du serveur Next, la clé est marquée `server-only` et aucune variable n'est préfixée
> `NEXT_PUBLIC_`. Et je l'ai vérifié en cherchant la clé dans le bundle construit — elle n'y
> est pas.

### 19. « Racontez-moi un incident. »
Prendre celui du 405, il est complet et court.

> En pleine démonstration, la bascule de profil sur la page de résultat renvoyait 405.
> La page était rendue par un POST, et le lien de bascule faisait un GET. J'ai ajouté un
> handler GET partageant le rendu avec le POST, construit les liens côté serveur, et écrit
> six tests de non-régression — que j'ai vérifiés en retirant le correctif.

### 20. « Qu'est-ce que vous retenez du projet ? »
La réponse à préparer par cœur, c'est la conclusion.

> Quatre incidents sur cinq avaient la même cause : la documentation affirmait ce que le code
> ne faisait pas. Mon registre RGPD annonçait une minimisation que l'API ne respectait plus,
> ma documentation annonçait un versionnement qui n'était pas branché. C'est pour ça que
> j'ai écrit une porte de conformité de douze critères qui **rejoue** la chaîne d'entraînement
> au lieu d'inspecter un artefact : un artefact valide ne prouve que le passé.

### 21. « Qu'auriez-vous fait avec plus de temps ? »
> Trois choses, dans cet ordre. Un jeu de validation annoté par un tiers, pour sortir de la
> circularité de mes métriques. La détection de dérive automatisée en tâche planifiée, elle
> est aujourd'hui déclenchée à la main. Et le rapprochement partitionné par commune, pour
> qu'il tienne à l'échelle de la base ADEME complète.

### 22. « Qu'est-ce qui vous a le plus surpris ? »
> Que mon propre dispositif de vérification ait un angle mort. J'avais allégé une dépendance,
> ce qui cassait la chaîne d'entraînement — et la porte de conformité répondait quand même
> CONFORME, parce qu'elle validait un artefact existant, donc le passé. J'ai ajouté un critère
> qui réentraîne dans un répertoire temporaire à chaque passage.

---

## F. Si on te compare à un autre candidat

Ne jamais dénigrer. Recentrer sur l'objet.

> Nos projets ne répondent pas à la même question. Beaucoup de projets prédisent ; le mien
> qualifie la donnée sur laquelle une prédiction s'appuierait. C'est un travail moins
> spectaculaire et plus en amont, et je l'ai choisi parce que c'est celui qu'on saute le
> plus souvent.

---

## G. Réflexes

- **Un chiffre, une preuve.** Chaque nombre annoncé a une commande ou un fichier derrière.
  Si on te demande d'où il vient, tu le régénères.
- **Les limites, tu les donnes en premier.** Métriques circulaires, base DPE non
  représentative, ambiguïté en copropriété, aucune prédiction de prix. Les annoncer désarme.
- **Si la démonstration casse :** `./scripts/soutenance.sh check`, puis l'application de
  repli sur `http://127.0.0.1:8000/`. Et le dire calmement — une panne gérée se note mieux
  qu'une panne cachée.
- **Ne pas meubler.** Une réponse de trois phrases qui répond vaut mieux qu'une de trente
  qui contourne.
