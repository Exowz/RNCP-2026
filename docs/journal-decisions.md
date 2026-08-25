# Journal de decisions techniques

Une ligne par decision structurante : la date, la decision, l'alternative ecartee, la raison.
Ce journal est une preuve pour **C16** (conduite de projet) et alimente la section 5 des cinq
rapports (« Bilan, limites, decisions »).

Format : `AAAA-MM-JJ HH:MM | DECISION | ALTERNATIVE ECARTEE | RAISON`

---

## 2026-08-24 — Jour 1 : socle

**J1-01 — Un seul depot, deux livrables.**
Le socle technique est le projet de substitution n°21 « Secure MLOps » ; le domaine metier est un
moteur d'anomalie / coherence / confiance sur le croisement DVF+ x DPE x Georisques.
*Ecarte* : deux projets separes. *Raison* : trois jours seul. Un systeme etroit, complet et
demontrable vaut mieux que deux systemes troues. Les deux soutenances sont separees par des tags Git,
pas par des depots.

**J1-02 — Python 3.12, pas 3.13 ni 3.9.**
*Ecarte* : le Python 3.9 du systeme (trop ancien pour `pydantic-settings` et la syntaxe moderne des
types) ; Python 3.13 (roues PySpark 3.5 incompletes).
*Raison* : 3.12 est le plus grand denominateur commun entre PySpark 3.5, PyTorch 2.x, MLflow 3 et
Evidently 0.7. Contrainte inscrite dans `pyproject.toml` (`>=3.12,<3.13`) : elle est verifiee, pas
esperee.

**J1-03 — JDK 17 installe explicitement pour Spark.**
La machine ne portait qu'un JDK 26. Spark 3.5 ne supporte officiellement que Java 8/11/17.
*Raison* : la panne serait apparue au pire moment (C1 « systeme big data », C2 « Spark SQL »).
`JAVA_HOME` est fige dans `scripts/spark-env.sh` et non laisse au hasard de la machine.

**J1-04 — Gestionnaire de paquets `uv`, verrou `uv.lock` versionne.**
*Ecarte* : `pip` + `requirements.txt` (resolution non deterministe), Poetry (plus lent).
*Raison* : reproductibilite exacte hors ligne. Le verrou fige les versions transitives ; la CI et la
machine de demonstration installent le meme graphe de dependances, a l'octet pres.

**J1-05 — Garde-fou hors ligne applicatif (`src/concorde/common/offline.py`).**
*Ecarte* : « couper le Wi-Fi le jour J ».
*Raison* : couper le reseau ne *prouve* rien et ne revele une dependance cachee qu'en soutenance.
Le verrou intercepte la couche socket et transforme toute sortie reseau non locale en erreur
explicite et localisee. C'est une preuve reproductible (`tests/test_offline_guard.py`), pas une
promesse.

**J1-06 — Journalisation JSON Lines avec pseudonymisation a l'ecriture.**
*Ecarte* : logs texte libre.
*Raison* : (1) exploitables par `jq` sans parsing fragile (C20) ; (2) un `request_id` traverse
app -> API -> modele, ce qui rend un incident rejouable (C21) ; (3) les champs personnels sont
haches **avant** ecriture disque, pour que le fichier de log ne devienne pas une base de donnees
personnelles clandestine (RGPD, C4/C20).

**J1-07 — Application en FastAPI + Jinja2 + CSS ecrit a la main.**
*Ecarte* : Streamlit (accessibilite non maitrisable, DOM genere) ; React/Vue (chaine de build npm,
risque de CDN, temps).
*Raison* : C14 et C17 exigent des preuves d'accessibilite WCAG/RGAA — reperes ARIA, ordre de
tabulation, contrastes, libelles de formulaire. Cela suppose de maitriser le HTML produit. Aucun
actif distant : tout est servi en local, ce qui satisfait la contrainte hors ligne.

## 2026-08-25 — Jour 2 : second client API

2026-08-25 12:20 | Le front Next.js lit les APIs Concorde uniquement depuis des Server Components avec une cle `CONCORDE_API_KEY` non publique | Appel direct depuis le navigateur ou cle `NEXT_PUBLIC_` | La cle reste dans l'environnement du serveur, le navigateur ne parle jamais aux ports Python et aucun CORS n'est necessaire.

2026-08-25 12:20 | L'API data expose une presentation lisible distincte de la charge `donnees` validable par `/predict` | Ajouter des champs d'affichage au contrat strict de prediction | Les noms de commune, l'adresse BAN et l'etiquette DPE sont accessibles sans introduire de champs inconnus dans le POST de prediction.

2026-08-25 12:20 | Le niveau de confiance de la liste reutilise les variables et la regle du moteur | Approximation propre a l'API data | Un filtre de liste ne doit pas annoncer une confiance differente du verdict obtenu ensuite pour le meme rapprochement.

2026-08-25 15:40 | La livraison est bloquee par une porte de conformite executable generant JSON et Markdown | Tableau Markdown saisi manuellement | Un rapport date doit etre la consequence des mesures qualite, robustesse et securite, et non une declaration invérifiable.

2026-08-25 15:40 | DVC suit le parquet rapproche et l'artefact PyTorch avec un remote dans `.dvc-local-remote/` | Retirer DVC de la pile ou configurer un remote distant | DVC est une brique imposee du projet de substitution et le stockage local conserve la demonstration hors ligne.

2026-08-25 15:40 | `PYSEC-2026-2447` est une exception temporaire et documentee | Masquer l'audit ou supprimer DVC sans trace | `diskcache` est transitive a DVC et ne dispose pas de correctif liste; toute autre vulnerabilite reste bloquante.

2026-08-25 15:50 | `mlflow-skinny` remplace la distribution MLflow complete | Conserver `mlflow` et bloquer cryptography sous 50 | Le projet n'utilise que le tracking SQLite; l'edition skinny garde cette API et permet de corriger `PYSEC-2026-3552`.

2026-08-25 16:00 | Les dependances directes sans usage (`requests`, `rich`, `tenacity`, `duckdb`) sont retirees | Les conserver par precaution | Une dependance non justifiee augmente la surface d'attaque, le temps de resolution et le bruit d'audit sans apporter de capacite au projet.

2026-08-25 19:10 | Le second client Next.js adopte un atlas cadastral local pour expliquer la convergence DVF+/DPE | Carte distante, imagerie satellite ou dashboard de scores | Des traits abstraits rendent le rapprochement compréhensible sans prétendre localiser un logement. La composition reste intégralement disponible hors ligne et les valeurs demeurent servies par les APIs.

2026-08-25 21:15 | LM Studio reformule une projection minimale du verdict sur `/expliquer`, hors de `/predict` | Confier la production du verdict au LLM ou intégrer l'appel à la prédiction | Le moteur demeure l'unique autorité de calcul. Le texte local est borné, identifié, échappé par React et remplaçable par l'explication assemblée si le service est absent.

2026-08-25 21:15 | La veille est distribuée dans un OPML local avec pages manuelles explicites quand un flux RSS n'existe pas | Service d'agrégation cloud ou faux flux RSS | La démonstration doit rester hors ligne et vérifiable. Les flux ADEME, CNIL, PyPI et GitHub sont importables; data.gouv.fr et Géorisques sont conservés comme consultations officielles sans promettre un flux inexistant.

2026-08-25 21:35 | Le LLM reçoit une consigne de rédaction déterminée par le code, pas le verdict à reformuler | Envoyer scores, motifs et réserves au modèle local | Gemma 4/MLX a produit une chaîne de raisonnement instable et a inversé une conclusion lors d'un essai long. Le code conserve donc tout sens métier et ne laisse au modèle qu'une phrase courte, contrôlée et réversible.

2026-08-25 21:35 | Les réponses LM Studio hors délai, incomplètes ou contenant du raisonnement deviennent des replis mesurés | Augmenter le délai jusqu'à obtenir une réponse ou afficher le texte non fiable | Le délai de 3 secondes protège la restitution; le taux de repli est une preuve de fiabilité et le texte assemblé demeure la référence.

2026-08-25 21:35 | Le prévol charge Gemma avec TTL d'une heure puis contrôle `lms ps` | S'appuyer sur un modèle potentiellement froid ou sur la seule sonde HTTP | Les latences observées varient de 18,9 s à 0,34 s à froid; l'état du serveur ne suffit pas à garantir que le modèle attendu est prêt.
