# E2 — Installation et configuration du service d'IA préconisé

**Compétences C6 à C8 · 15 minutes · quatrième épreuve du passage**

Bandeau : `Compétences prouvées : Cx`. Rythme visé ~135 mots/minute.

> **Position particulière** : cette épreuve arrive **après** les deux démonstrations. Le jury a déjà
> vu le système tourner. C'est un avantage : on ne défend pas un choix théorique, on explique un
> choix dont ils ont constaté le résultat. **L'assumer explicitement en slide 1.**

---

## Slide 1 — Le chemin que je vais suivre · 45 s

**Sur la slide**
> **Besoin → veille → alternatives → choix → paramétrage → test → limites mesurées**
>
> Vous venez de voir le service tourner dans l'application. Je reviens maintenant sur
> **comment j'y suis arrivé** — et sur ce que j'ai mesuré avant de lui faire confiance.

**Script**
> Cette épreuve porte sur le service d'intelligence artificielle : comment je l'ai choisi, installé
> et configuré.
>
> Elle arrive après les deux démonstrations, ce qui me va bien : vous avez déjà vu le service
> tourner dans l'application. Je ne vais donc pas défendre un choix théorique, je vais expliquer
> comment j'y suis arrivé, et surtout ce que j'ai mesuré avant de lui faire confiance.
>
> Je suivrai le chemin complet : le besoin reformulé, la veille qui l'encadre, les alternatives
> comparées, le choix, le paramétrage, et les limites que j'ai constatées.

---

## Slide 2 — C7 : le besoin reformulé · 1 min 45

**Sur la slide**
> **Contexte métier** — le verdict est calculé, exact, mais rédigé par assemblage de conditions.
> Un particulier lit mieux une phrase qu'une juxtaposition de scores.
>
> | | |
> |---|---|
> | **Entrées** | le verdict **déjà calculé** : niveau d'anomalie, cohérence, confiance, nombre de motifs |
> | **Sorties** | **une phrase** en français courant + la **provenance** du texte |
> | **Ce qui n'entre jamais** | données brutes, adresse, parcelle, identifiants |
> | **Ce qui ne sort jamais** | un score, un chiffre, un jugement |
>
> **Critère de réussite** : la phrase est lisible, **conforme au verdict**, produite en < 3 s, et
> son échec ne dégrade jamais le service.

**Script**
> Le besoin d'abord, parce que c'est lui qui commande le reste.
>
> Le verdict que produit Concorde est exact, mais il est rédigé par assemblage de conditions : « une
> contradiction majeure détectée, cohérence 60 %, les données permettent de le dire avec un bon
> niveau de certitude ». C'est juste, mais c'est écrit par une machine, et un particulier lit mieux
> une phrase.
>
> Le besoin est donc précis : reformuler en français courant un verdict **déjà calculé**. J'insiste
> sur « déjà calculé », parce que c'est ce qui définit la frontière.
>
> En entrée, le service reçoit uniquement le verdict : niveaux, scores, nombre de motifs. Jamais
> les données brutes, jamais une adresse, jamais une parcelle. En sortie, il produit une phrase et
> rien d'autre : aucun score, aucun chiffre, aucun jugement.
>
> Et le critère de réussite est explicite : la phrase doit être lisible, conforme au verdict,
> produite en moins de trois secondes, et son échec ne doit jamais dégrader le service.

---

## Slide 3 — C6 : la veille, et sa qualification · 2 min

**Sur la slide**
> **Agrégation réellement configurée** : [`docs/veille.opml`](../../docs/veille.opml) — importable dans un lecteur RSS local.
> Flux : ADEME (Bâtiment) · CNIL · PyPI · GitHub releases DVC et MLflow.
>
> **Grille de fiabilité — six critères par source** :
> `auteur` · `date` · `source primaire` · `convergence` · `accessibilité` · `biais`
>
> | Source | Biais identifié |
> |---|---|
> | ADEME | vue institutionnelle, **pas une mesure exhaustive du parc** |
> | Géorisques | granularité communale, **ne remplace pas une expertise parcellaire** |
> | PyPI | **publication ≠ correctif de sécurité** |
> | GitHub releases | annonce éditeur, à vérifier avant montée de version |
>
> ⚠️ **data.gouv.fr et Géorisques n'ont pas de flux RSS stable** — URL testées, réponse 404.
> Conservées comme pages de consultation, **pas présentées comme des flux.**

**Script**
> La veille, maintenant. Le coaching est explicite sur ce point : accumuler des liens sans expliquer
> leur fiabilité ne prouve pas la compétence.
>
> J'ai donc deux choses. D'abord un outil d'agrégation réellement configuré : un fichier OPML
> importable dans un lecteur RSS local, qui contient les flux officiels de l'ADEME, de la CNIL, de
> PyPI et des dépôts GitHub de mes dépendances critiques.
>
> Ensuite une grille de qualification. Chaque source est évaluée sur six critères : qui publie, la
> date, s'il s'agit d'une source primaire, si l'information converge avec d'autres, si elle est
> accessible, et quel est son biais.
>
> Ce dernier critère est celui que je trouve le plus utile. L'ADEME est une source primaire
> excellente, mais sa base DPE n'est pas un échantillon représentatif du parc français — l'agence le
> dit elle-même. C'est ce biais identifié qui m'a conduit à afficher des réserves partout dans
> l'application plutôt qu'à présenter un DPE comme une vérité.
>
> Un point d'honnêteté : data.gouv.fr et Géorisques ne publient pas de flux RSS stable pour les jeux
> que je suis. J'ai testé les URL candidates, elles répondent 404. Je les conserve comme pages de
> consultation manuelle, et je ne les présente pas comme des flux. C'était plus simple d'invoquer un
> service d'agrégation en ligne que je n'ai pas configuré — je préfère une limite visible.

---

## Slide 4 — C6 : le rythme et ce qu'il déclenche · 1 min

**Sur la slide**
> **Rythme** : chaque matin jusqu'à la soutenance, puis hebdomadaire.
>
> Une alerte qui touche **le contrat, la sécurité, une source ou une dépendance** déclenche :
> → une entrée datée dans `docs/journal-decisions.md`
> → une preuve adaptée
> → si nécessaire, **un incident documenté**
>
> **Une source ne devient jamais une exigence automatique** : elle est interprétée dans le périmètre du projet.
>
> **Limite assumée** : pas d'animation d'équipe. Je suis seul. Aucun collectif n'est simulé.

**Script**
> Sur le rythme : revue quotidienne jusqu'à la soutenance, puis hebdomadaire.
>
> Ce que je veux souligner, c'est ce qu'une alerte déclenche. Elle n'est pas simplement lue : si
> elle touche le contrat, la sécurité, une source ou une dépendance, elle produit une entrée datée
> dans mon journal de décisions, une preuve adaptée, et si nécessaire un incident documenté.
>
> Le principe que je m'impose : une source ne devient jamais une exigence automatique. Elle est
> interprétée dans le périmètre du projet, et la décision qui en découle est tracée avec sa raison.
>
> Et je dois annoncer une limite. Le référentiel attend une veille qui **anime un travail collectif**
> — sélection des sources, partage des synthèses aux parties prenantes. Je suis seul. Je ne simule
> aucune équipe : la compétence est donc partiellement couverte, et je préfère vous le dire
> plutôt que vous laisser le découvrir.

---

## Slide 5 — C7 : la matrice de comparaison · 1 min 45

**Sur la slide**

| Service | Fonctionnel | Technique | Risque | Décision |
|---|---|---|---|---|
| **LM Studio + Gemma 4B** | rédige une phrase à partir d'une consigne choisie par le code | HTTP local, modèle réchauffé, `temperature=0`, 90 tokens, 3 s | fuite de raisonnement ou dépassement : **2 réponses sur 3** en mesure à chaud | **Retenu sous garde-fou** |
| Ollama | capacité comparable | local possible mais **non installé, sans modèle chargé** | téléchargement d'un poids : temps, stockage, dépendance de démo | **Écarté** |
| API LLM cloud | qualité possiblement élevée | réseau, clé fournisseur, disponibilité d'un tiers | transfert de prompts, coût variable, **indisponible hors ligne** | **Écarté** |
| Auto-encodeur interne | évalue anomalie, cohérence, confiance | déjà présent | le détourner **confondrait calcul et restitution** | **Écarté pour la reformulation** |

**Script**
> La matrice de comparaison, sur quatre axes : l'adéquation fonctionnelle, la faisabilité technique,
> le risque, et la décision.
>
> LM Studio avec Gemma 4B est retenu, mais notez la formule : **retenu sous garde-fou**. J'y reviens
> dans deux slides, parce que le risque que j'ai mesuré est réel.
>
> Ollama est écarté non pas pour une faiblesse fonctionnelle — il ferait la même chose — mais parce
> qu'il n'est pas installé et qu'aucun modèle n'y est chargé. Le télécharger ajouterait du temps,
> du stockage et une dépendance de démonstration, pour zéro valeur supplémentaire.
>
> Les API cloud sont écartées frontalement : elles contredisent mes contraintes. Elles exigent un
> réseau, transfèrent mes prompts à un tiers, coûtent de façon variable, et sont indisponibles hors
> ligne.
>
> Et le dernier est intéressant : mon propre auto-encodeur. Il est déjà là et il est excellent pour
> ce qu'il fait. Je l'écarte quand même pour la reformulation, parce que le détourner en générateur
> de texte confondrait le calcul du verdict et sa restitution. Ces deux responsabilités doivent
> rester séparées.

---

## Slide 6 — C8 : installation et paramétrage · 1 min 30

**Sur la slide**
```bash
lms load google/gemma-4-e4b --ttl 3600 -y   # préchargé : évite le démarrage à froid
lms server start                             # API OpenAI-compatible sur 127.0.0.1:1234
curl http://127.0.0.1:1234/v1/models         # vérification du modèle exact
```
> | Paramètre | Valeur | Pourquoi |
> |---|---|---|
> | `temperature` | **0** | reproductibilité : même consigne → même phrase |
> | `max_tokens` | **90** | une phrase suffit ; borne le coût et la latence |
> | délai HTTP | **3 s** | au-delà, le repli est meilleur que l'attente |
> | liaison | **`127.0.0.1`** | seul l'utilisateur de la machine y accède ; aucune donnée ne sort |
> | TTL | **3600 s** | le modèle reste résident : évite 18 s de repagination |

**Script**
> L'installation et le paramétrage. Le service est LM Studio, qui expose une API compatible OpenAI
> sur la boucle locale. Le modèle, Gemma 4B en quatre bits, est déjà présent sur le disque : rien
> n'est téléchargé au moment de la démonstration.
>
> Cinq paramètres, chacun justifié. La température à zéro, pour la reproductibilité : la même
> consigne doit produire la même phrase. Quatre-vingt-dix tokens, parce qu'une phrase suffit et que
> ça borne à la fois le coût et la latence. Un délai HTTP de trois secondes, au-delà duquel le
> repli vaut mieux que l'attente.
>
> La liaison à `127.0.0.1` est un choix de sécurité : seul l'utilisateur de la machine peut
> atteindre le service, et aucune donnée Concorde ne quitte le poste.
>
> Et le TTL d'une heure : je l'ai ajouté après une mesure. Le modèle se décharge après inactivité,
> et le premier appel suivant prend dix-huit secondes de repagination. En le maintenant résident, on
> passe à moins d'une seconde.

---

## Slide 7 — C8 : ce que j'ai mesuré avant de faire confiance · 2 min 15

**Sur la slide**
> **Mesure 1 — le démarrage à froid** (même requête triviale, répétée)
> `18,9 s` → `8,5 s` → **`0,34 s`** — ce n'était pas le modèle qui était lent, c'était son chargement.
>
> **Mesure 2 — quatre paramètres testés pour désactiver le raisonnement**
> `reasoning_effort:"none"` → le raisonnement passe dans `content` · `"low"`, `reasoning:{enabled:false}`,
> `chat_template_kwargs` → **sans effet**. Bug amont connu : `lmstudio-ai/mlx-engine#337`.
>
> **Mesure 3 — la forme de la consigne décide**
> « **Reformule ce verdict** : … » → analyse → 551 tokens de raisonnement, **31,6 s**
> « **Écris une phrase disant que** X » → rédaction → 0 token, **0,5 s**
>
> **Mesure 4 — l'inversion**
> Consigne d'interprétation, budget suffisant : le modèle a répondu
> « le rapprochement est jugé **cohérent** » sur un verdict à **cohérence 60 % et contradiction majeure**.

**Script**
> Voici la partie dont je suis le plus satisfait, parce qu'elle explique pourquoi le service est
> « retenu **sous garde-fou** ».
>
> Première mesure : j'ai cru que le modèle était lent. En répétant la même requête triviale, j'ai
> obtenu dix-huit secondes, puis huit, puis un tiers de seconde. Ce n'était pas le modèle, c'était
> sa repagination en mémoire. D'où le TTL.
>
> Deuxième mesure : Gemma 4 sur moteur MLX déclenche un mode raisonnement qui consomme tout le
> budget de tokens et laisse la réponse vide. J'ai testé quatre paramètres pour le désactiver.
> Aucun ne fonctionne proprement — c'est un bug amont documenté, que je cite dans ma veille.
>
> Troisième mesure, et c'est la découverte utile : c'est la **forme de la consigne** qui décide.
> Demandez au modèle de « reformuler ce verdict », il analyse, consomme 551 tokens de raisonnement
> et met trente et une secondes. Demandez-lui d'« écrire une phrase disant que X », il rédige, en un
> demi-seconde, sans raisonner.
>
> Et la quatrième mesure est celle qui a fixé l'architecture. Quand je lui ai donné un verdict à
> interpréter avec un budget suffisant, il a répondu que « le rapprochement est jugé cohérent » —
> alors que le verdict transmis était une cohérence de 60 % avec une contradiction majeure. **Il
> avait inversé le sens.**

---

## Slide 8 — C8 : la conception qui en découle · 1 min 45

**Sur la slide**
> ```
> verdict calculé ──► le CODE choisit la consigne ──► LLM rédige ──► {texte, source:"modele_local"}
>                                                          │
>          délai > 3 s · sortie vide · raisonnement · erreur HTTP
>                                                          │
>                                                          └──► texte assemblé  {source:"texte_assemble"}
> ```
> **Est compté comme échec** : délai dépassé · `content` vide ou < 15 caractères ·
> `finish_reason ≠ stop` · `reasoning_tokens > 0` · toute erreur HTTP
>
> **Le taux de repli est mesuré et exposé** dans `monitoring/model/metriques_lm_studio.json`.
> Les scores et les motifs restent affichés **à côté** : toute divergence est visible.
> Sortie **bornée, échappée, jamais rendue en HTML**.

**Script**
> De ces mesures découle toute la conception.
>
> Le code choisit la consigne en fonction du verdict déjà calculé. Le modèle ne reçoit qu'une
> **instruction de rédaction** : il ne peut pas inverser un sens qu'on ne lui demande pas d'établir.
> C'est la parade directe à la quatrième mesure.
>
> Cinq conditions déclenchent le repli : délai dépassé, sortie vide ou trop courte, arrêt anormal,
> présence de tokens de raisonnement, ou erreur HTTP. Dans tous ces cas, l'utilisateur reçoit le
> texte assemblé, et la réponse indique sa provenance.
>
> Le taux de repli est mesuré et exposé dans les métriques. Ce n'est pas un aveu de faiblesse :
> c'est un instrument. Un service dont on chiffre la fiabilité vaut mieux qu'un service dont on
> affirme qu'il marche.
>
> Enfin, deux précautions. La sortie du modèle est traitée comme du contenu **non fiable** : bornée,
> échappée, jamais rendue comme du HTML. Et les scores et les motifs restent affichés à côté du
> texte, inchangés — si le modèle dérive, l'écart se voit immédiatement.

---

## Slide 8 bis — C8 : le service est surveillé, pas seulement branché · 1 min 30

**Sur la slide**
> Avant **tout** appel : `ClientLMStudio.verifier_service()` exige **le modèle exact**,
> pas seulement un serveur qui répond.
>
> Écrit à chaque vérification :
> — un événement JSON Lines `service_ia_verifie`
> — `monitoring/model/metriques_lm_studio.json` : appels · erreurs · latence · **taux de repli**
>
> Si le serveur ou le modèle manque → **erreur explicite**, jamais un appel silencieux vers le vide.
>
> **Ce qui est monitoré est ce qu'on peut défendre.** Un service dont on ne mesure rien ne se
> distingue pas d'un service qui ne marche pas.

**Script**
> Dernier volet de C8 : le monitorage du service, parce que l'installer ne suffit pas.
>
> Avant tout appel, un contrôle vérifie non pas qu'un serveur répond, mais que **le modèle exact
> attendu** est exposé. C'est une distinction qui compte : LM Studio peut très bien tourner avec un
> autre modèle chargé, et mes consignes sont calibrées pour celui-ci. Un serveur qui répond n'est
> pas une garantie.
>
> Chaque vérification écrit un événement dans les journaux structurés, et un fichier de métriques
> qui accumule les appels, les erreurs, la latence et le taux de repli.
>
> Ce taux de repli est l'indicateur que je regarde. Il ne cache pas la fragilité du modèle, il la
> chiffre. Et c'est ce qui me permet de dire aujourd'hui « deux réponses acceptées sur trois en
> mesure à chaud » plutôt que « ça marche généralement ».
>
> Enfin, en cas d'absence du serveur ou du modèle, l'erreur est explicite et nommée. Il n'y a jamais
> d'appel silencieux vers le vide, ni de résultat vaguement dégradé sans que personne ne le sache.

---

## Slide 9 — Récapitulatif E2 · 45 s

**Sur la slide**

| | Preuve | Où |
|---|---|---|
| **C6** | OPML configuré, grille à 6 critères, rythme, déclencheurs — **collectif partiel assumé** | `docs/veille.md`, `docs/veille.opml` |
| **C7** | Besoin reformulé, matrice à 4 axes, **3 services écartés avec motif** | `docs/benchmark.md` |
| **C8** | Installation, 5 paramètres justifiés, monitoring, **limites mesurées et repli conçu** | `docs/service-ia.md` |

**Script**
> Pour résumer : une veille avec un outil réellement configuré et une grille de qualification à six
> critères ; un besoin reformulé avant tout choix ; une matrice qui compare quatre options sur
> quatre axes et en écarte trois avec leur motif ; et un service installé, paramétré, monitoré,
> dont j'ai **mesuré les limites avant de lui faire confiance**, et pour lequel j'ai conçu un repli.
>
> La leçon que j'en retire, et qui vaut au-delà de ce projet : **on n'intègre pas un service d'IA
> sur sa réputation, on l'intègre sur ce qu'on a mesuré.**
>
> Je passe au monitorage et à la résolution d'incident.

---

## Aide-mémoire

**À montrer si on te le demande**
- l'OPML : `cat docs/veille.opml`
- la grille de fiabilité : `docs/veille.md`
- le service répond : `curl http://127.0.0.1:1234/v1/models`
- le repli en direct : arrêter LM Studio → l'application continue, `source: "texte_assemble"`

**Questions probables**
- *Pourquoi pas une API cloud, plus performante ?* → elle contredit trois de mes contraintes : hors ligne, RGPD (transfert de prompts à un tiers), et coût variable. La qualité supérieure ne compense pas.
- *À quoi sert votre LLM, concrètement ?* → à mettre en phrase, jamais à juger. Et je peux vous montrer ce qui arrive quand on lui demande de juger : il a inversé un verdict.
- *Votre taux de repli est élevé, n'est-ce pas un échec ?* → c'est une mesure. Le service est retenu **sous garde-fou** précisément parce que je l'ai mesuré. Un repli compté vaut mieux qu'une confiance supposée.
- *Et la veille collective ?* → je suis seul, je ne simule pas d'équipe. C6 est partiellement couverte et je l'assume.
