# E3 — Mise en service du modèle et chaîne MLOps

**Compétences C9 à C13 · 20 minutes · avec démonstration · deuxième épreuve du passage**

Bandeau : `Compétences prouvées : Cx`. Rythme visé ~135 mots/minute.
**Budget : 14 min de présentation + 5 min de démonstration + 1 min de transition.**

> ⚠️ **Avant de commencer** — les quatre services doivent tourner et être vérifiés.
> Voir l'aide-mémoire en fin de document. **Ne rien lancer devant le jury.**

---

## Slide 1 — Le cadre imposé et ce que je livre · 45 s

**Sur la slide**
> **E3 — Mise en service d'un modèle fourni, intégré à une application existante**
>
> Mise en scène assumée : l'équipe Data Science livre à l'équipe applicative
> **un artefact PyTorch gelé et versionné**, avec sa fiche.
>
> `models/concorde_moteur.pt` — version `0.1.0` · graine `20260824` · empreinte du jeu d'entraînement

**Script**
> Cette épreuve suppose un modèle fourni et une application existante. Mon dépôt est neuf, donc
> j'assume une mise en scène honnête : je me place à la frontière entre deux équipes. L'équipe Data
> Science livre un artefact PyTorch gelé et versionné, accompagné de sa fiche ; l'équipe applicative
> le met en service.
>
> Cette frontière n'est pas décorative : elle est matérialisée par un fichier unique, `concorde_moteur.pt`,
> qui contient tout ce qu'il faut pour rejouer une prédiction à l'identique. J'y reviens dans deux slides.

---

## Slide 2 — Le modèle : trois questions, jamais fusionnées · 1 min 30

**Sur la slide**
> | Axe | Question | Comment | Sortie |
> |---|---|---|---|
> | **Cohérence** | Les deux enregistrements se **contredisent**-ils ? | 5 règles métier seuillées | `score_coherence`, `motifs` |
> | **Anomalie** | Ce rapprochement **ressemble**-t-il aux autres ? | auto-encodeur PyTorch | `score_anomalie`, `variables_atypiques` |
> | **Confiance** | Peut-on **se fier** à cette réponse ? | complétude, géocodage, ambiguïté | `confiance.niveau`, `reserves` |
>
> **Aucune note unique.** Un rapprochement cohérent peut être peu fiable ; un rapprochement atypique peut être bien documenté.

**Script**
> Le modèle répond à trois questions, et je veux insister sur le fait qu'elles ne sont jamais
> fusionnées en une note unique.
>
> La cohérence demande si les deux enregistrements se contredisent : c'est une couche de règles
> métier explicites et seuillées. L'anomalie demande si ce rapprochement ressemble aux autres :
> c'est un auto-encodeur. La confiance demande si l'on peut se fier à la réponse elle-même : elle
> mesure ce qui manque.
>
> Pourquoi trois et pas un ? Parce que ce sont trois questions différentes. Un rapprochement peut
> être parfaitement cohérent et malgré tout peu fiable, parce qu'il manque la moitié des champs.
> Un autre peut être atypique tout en étant parfaitement documenté. Les fusionner en une note
> détruirait exactement l'information que le produit prétend fournir.
>
> Vous verrez en démonstration un cas où la cohérence est mauvaise et la confiance élevée. Cela
> veut dire : « je suis sûr qu'il y a un problème ». C'est une phrase que je ne pourrais pas dire
> avec un score unique.

---

## Slide 3 — Pourquoi un auto-encodeur · 1 min 30

**Sur la slide**
```python
class AutoEncodeur(nn.Module):
    def __init__(self, dim_entree: int, dim_cachee: int = 12, dim_latente: int = 3):
        self.encodeur = nn.Sequential(nn.Linear(dim_entree, dim_cachee), nn.ReLU(),
                                      nn.Linear(dim_cachee, dim_latente))
        self.decodeur = nn.Sequential(nn.Linear(dim_latente, dim_cachee), nn.ReLU(),
                                      nn.Linear(dim_cachee, dim_entree))
```
> **Aucune étiquette « rapprochement faux » n'existe** dans les données publiques → problème **non supervisé**.
> Le réseau apprend à reconstruire la structure majoritaire ; **ce qu'il reconstruit mal est atypique**.
> Goulot volontairement étroit (3 dimensions) : un réseau plus large **mémoriserait** les anomalies.
> Arrêt anticipé — un auto-encodeur trop entraîné finit par bien reconstruire les anomalies elles-mêmes.

**Script**
> Pourquoi un auto-encodeur, et pas une classification ? Parce qu'il n'existe aucune étiquette
> « ce rapprochement est faux » dans les données publiques. Personne n'a annoté les appariements.
> Le problème est donc non supervisé par nature.
>
> Le principe : le réseau apprend à comprimer puis reconstruire la structure majoritaire des
> rapprochements. Ce qu'il reconstruit mal est, par construction, ce qui ne ressemble pas au reste.
>
> Deux choix d'architecture méritent une justification. Le goulot est volontairement étroit — trois
> dimensions : un réseau plus large mémoriserait les anomalies au lieu de les manquer, et l'erreur
> de reconstruction s'effondrerait précisément sur les lignes que je cherche à isoler. Et
> l'entraînement s'arrête par arrêt anticipé sur la perte de validation, pour la même raison : un
> auto-encodeur trop entraîné finit par reconstruire correctement les anomalies, et perd sa raison
> d'être.
>
> Dernier point qui compte pour l'explicabilité : l'erreur se décompose **par variable**. Le modèle
> ne dit pas seulement « cette ligne est atypique », il dit **quelle dimension** l'est.

---

## Slide 4 — La métrique honnête · 1 min 30

**Sur la slide**
> | Métrique | Valeur | Lecture |
> |---|---:|---|
> | **AUC auto-encodeur** | **0,9095** | **Informatif** — il n'a vu ni les règles ni les étiquettes |
> | Average precision | 0,8427 | Informatif, robuste au déséquilibre |
> | Rappel des règles | 0,5769 | ⚠️ **Circulaire** — publié, mais **pas une performance** |
> | Système complet (précision / rappel) | 0,889 / 0,615 | Tel qu'il alerte en production |
>
> Jeu de test : 108 lignes · taux de base d'anomalies : 24,1 %

**Script**
> Voici les métriques, et je veux être précis sur ce qui est informatif et ce qui ne l'est pas.
>
> Le jeu de démonstration porte des anomalies plantées, et mes règles de cohérence visent les mêmes
> familles de contradictions. Le rappel des règles est donc **circulaire** : il mesure la cohérence
> de mon générateur avec lui-même, pas une performance. Je le publie par transparence, et je ne le
> présente jamais comme un résultat.
>
> La métrique informative est l'AUC de l'auto-encodeur seul : 0,91. Elle l'est parce que
> l'auto-encodeur n'a vu ni les règles, ni les étiquettes — il n'a appris que la structure des
> données. Un pouvoir de tri de 0,91 sur un problème non supervisé est un bon résultat.
>
> Détail intéressant : l'auto-encodeur trie mieux que mes règles ne rappellent. Autrement dit,
> l'apprentissage attrape des choses que je n'avais pas prévues en écrivant les règles. C'est
> exactement ce qu'on lui demande.

---

## Slide 4 bis — Les cinq règles, et d'où viennent leurs seuils · 1 min 45

**Sur la slide**

| ID | Règle | Gravité | Seuil | Fondement du seuil |
|---|---|---|---|---|
| `COH-01` | écart de surface DVF / DPE | **majeur** | > **20 %** | surface réelle bâtie ≠ surface habitable : un écart modéré est attendu |
| `COH-02` | désaccord sur le type de logement | **majeur** | maison ≠ appartement | les deux sources qualifient le bien ; un désaccord n'est pas une nuance |
| `COH-03` | DPE établi **après** la mutation | mineur | `date_DPE > date_vente` | le diagnostic ne décrit pas le bien tel qu'il a été vendu |
| `COH-04` | DPE antérieur de plus de 10 ans | mineur | > **10 ans** | **durée de validité réglementaire** d'un DPE |
| `COH-05` | prix au m² très éloigné de la médiane | mineur | **> +200 %** ou **< −70 %** | signale une vente non ordinaire : viager, démembrement, lot mal découpé |

> Majeur : −0,40 sur la cohérence · mineur : −0,15. **Aucun seuil n'est arbitraire.**

**Script**
> Je veux détailler les règles, parce que « seuillé » ne veut rien dire si les seuils sortent de
> nulle part.
>
> La première tolère 20 % d'écart entre la surface déclarée à la vente et la surface habitable du
> diagnostic. Pourquoi 20 ? Parce que ces deux notions ne mesurent pas la même chose : les combles,
> les sous-sols et les annexes comptent dans l'une et pas dans l'autre. Un écart modéré est donc
> **attendu**. Au-delà du seuil, l'explication la plus probable n'est plus une convention de mesure,
> c'est que les deux enregistrements décrivent deux logements différents.
>
> La quatrième est la plus facile à défendre : dix ans, c'est la durée de validité réglementaire
> d'un DPE. Le seuil n'est pas un choix, c'est le droit.
>
> La cinquième est celle qui touche au prix, et je précise immédiatement : le prix n'est **pas
> prédit**. Il sert uniquement de signal de cohérence. Un écart extrême à la médiane communale
> signale généralement une mutation qui n'est pas une vente ordinaire — un viager, un démembrement,
> une vente entre proches — plutôt qu'un bien exceptionnel.
>
> Enfin, les pondérations. Un motif majeur retire 0,40 à la cohérence, un mineur 0,15. Deux motifs
> majeurs suffisent donc à faire tomber le score à 20 %. C'est délibéré : deux contradictions
> sérieuses ne se compensent pas, elles s'additionnent.

---

## Slide 5 — L'artefact gelé : la frontière entre les deux équipes · 1 min 15

**Sur la slide**
> `models/concorde_moteur.pt` contient **tout** ce qui est nécessaire à rejouer une prédiction :
> — les poids · les moyennes et écarts-types de normalisation · les médianes d'imputation
> — les médianes de prix **communales de référence** · la grille de calibration
> — la table d'exposition aux aléas · la **fiche** : version, date, graine, empreinte du jeu, commit Git
>
> ```python
> if variables_artefact != VARIABLES_COMPARAISON:
>     raise ValueError("Le contrat de variables de l'artefact ne correspond pas au code courant.")
> ```
> → **Aucun accès réseau, aucune base, aucun recalcul sur les données de production.**

**Script**
> L'artefact contient tout : les poids, mais aussi les paramètres de normalisation, les médianes
> d'imputation, les médianes de prix communales de référence, la grille de calibration, et une fiche
> d'identité avec la version, la graine aléatoire, l'empreinte du jeu d'entraînement et le commit Git.
>
> Un point de méthode : les médianes communales sont **figées** dans l'artefact, calculées sur
> l'entraînement seul. Les recalculer à l'inférence ferait dépendre le score du lot de production —
> c'est une fuite, et cela rendrait la prédiction non reproductible.
>
> Et il y a un garde-fou au chargement : si le contrat de variables de l'artefact ne correspond
> plus au code, le service refuse de démarrer avec un message explicite plutôt que de servir des
> prédictions silencieusement fausses.
>
> Conséquence directe : servir le modèle ne demande aucun accès réseau. C'est ce qui rend la
> démonstration hors ligne possible.

---

## Slide 6 — C9 : l'API qui expose le modèle · 1 min 30

**Sur la slide**
```python
@app.post("/predict", response_model=VerdictSortie, tags=["prediction"],
          responses={401: {...}, 422: {...}, 503: {...}})
def predict(
    entree: RapprochementEntree,
    identite: Annotated[Identite, Depends(exige_role("reader"))],
    moteur:  Annotated[Moteur,   Depends(moteur_requis)],
) -> VerdictSortie:
```
```python
model_config = ConfigDict(
    extra="forbid",   # un champ inconnu est une erreur, pas un silence
)
```
> Routes : `/predict` · `/predict/lot` (rôle `analyst`, borné à 200) · `/regles` · `/modele/fiche` · `/metriques` · `/sante`
> **401** sans clé · **422** entrée invalide, champ fautif nommé · **503** artefact absent, message actionnable

**Script**
> L'API expose le modèle par six routes. Trois éléments sur celle-ci.
>
> `exige_role("reader")` impose une clé d'API valide et un rôle suffisant. Sans clé, la réponse est
> 401 — je vous le montrerai.
>
> `extra="forbid"` : un champ inconnu dans la charge utile est une erreur, pas un silence. J'ai fait
> ce choix volontairement, parce qu'un service qui « répare » discrètement une entrée douteuse
> produit un résultat que plus personne ne peut expliquer ensuite. C'est exactement le défaut que
> Concorde cherche à rendre visible chez les autres : je ne pouvais pas le commettre moi-même.
>
> Et `moteur_requis` : si l'artefact est absent, le service démarre quand même, se déclare
> « dégradé » sur sa sonde de santé, et répond 503 avec la commande exacte à exécuter. Un service
> qui refuse de démarrer ne dit pas ce qui lui manque ; celui-ci le dit.

---

## Slide 7 — C10 : deux clients indépendants de la même API · 1 min 15

**Sur la slide**
> ```
> navigateur ──► Next.js :3000 ──┐
>                                ├──► API modèle :8002 ──► artefact local
> navigateur ──► Jinja   :8000 ──┘
> ```
> **Aucun des deux n'importe le moteur.** Tous deux parlent HTTP.
> → Une API consommée par **deux clients indépendants** est un **contrat**, pas un utilitaire de gabarit.
>
> Dégradation prouvée : API arrêtée → page d'erreur `role="alert"`, **aucune trace technique**.
> Capture : `reports/captures/09-web-degradation-api-indisponible.jpg`

**Script**
> L'intégration, maintenant. Deux applications consomment cette API : une application rendue côté
> serveur en Jinja, et un front Next.js. Aucune des deux n'importe le moteur — toutes deux passent
> par HTTP.
>
> Ce n'est pas de la redondance gratuite. Une API consommée par deux clients indépendants cesse
> d'être un utilitaire de gabarit et devient un contrat : le découplage que j'annonce est
> démontrable, pas déclaré.
>
> Et j'ai testé la panne. Quand j'arrête l'API modèle, l'application n'affiche ni trace technique
> ni page blanche : elle affiche un message compréhensible, annoncé aux lecteurs d'écran, qui
> explique qu'aucun résultat ne peut être produit. Le choix est explicite : plutôt que d'avancer un
> résultat partiel, l'application préfère ne rien avancer.

---

## Slide 8 — C11 : monitorer le modèle · 1 min 15

**Sur la slide**
> | Ce qui est surveillé | Où |
> |---|---|
> | **Dérive** des variables (Evidently) | `monitoring/model/evidently_drift.html` + `.json` |
> | **Latence** p50 / p95 / max, par route | `/metriques` |
> | **Taux d'erreur** par route | `/metriques` |
> | Répartition des verdicts et des niveaux de confiance | compteurs |
> | **Alertes** : p95 > 750 ms · taux d'erreur > 5 % | évaluées à partir de 5 appels |
>
> **Aucune action automatique sur alerte.** Une dérive déclenche une **revue humaine**, jamais un réentraînement.

**Script**
> Le monitoring du modèle couvre quatre choses : la dérive des variables, la latence, les erreurs,
> et la répartition des verdicts.
>
> La dérive est produite par Evidently, en local, sous forme d'un rapport HTML et d'un JSON
> exploitable. Les latences sont mesurées par route, en p50, p95 et maximum, sur une fenêtre
> glissante. Deux seuils déclenchent des alertes : un p95 au-dessus de 750 millisecondes, un taux
> d'erreur au-dessus de 5 %. Ils ne sont évalués qu'à partir de cinq appels, pour ne pas alerter
> sur un échantillon d'un seul point.
>
> Un choix que je veux souligner : **aucune action automatique n'est déclenchée par une alerte**.
> Une dérive détectée provoque une revue humaine, jamais un réentraînement automatique. Réentraîner
> automatiquement sur des données dérivées, c'est apprendre la dérive.

---

## Slide 9 — C12 : les tests · 1 min 15

**Sur la slide**
> **54 tests · 86 % de couverture · `pytest -m "not local_service"`**
>
> | Famille | Ce qui est vérifié |
> |---|---|
> | Données | formats, schémas, règles de nettoyage, Spark, PostgreSQL |
> | Modèle | entraînement, évaluation, écriture **et rechargement** d'artefact |
> | **Robustesse** | perturbation, valeurs aux bornes, champs absents, **déterminisme** |
> | API | 401 sans clé, 422 champ inconnu, contrat des trois axes |
> | Application | hors ligne, accessibilité, bascule de profil, dégradation |
> | **Non-régression** | 5 incidents réels, marqueur `regression` |
>
> Un test rendu hermétique est **vérifié dans les deux sens** : on retire le correctif, il doit échouer.

**Script**
> Cinquante-quatre tests, 86 % de couverture. Ils couvrent six familles : les données, le modèle,
> la robustesse, l'API, l'application, et la non-régression sur incidents.
>
> Deux points de méthode. Le test du modèle ne se contente pas d'entraîner : il écrit un artefact
> temporaire **et le recharge**, parce que c'est le rechargement qui casse en pratique, pas
> l'entraînement.
>
> Et sur la non-régression, j'applique une règle systématique : **vérifier dans les deux sens**.
> Quand j'écris un test qui doit attraper un bug, je retire le correctif et je confirme que le test
> échoue bien. Un test de non-régression qui passe avant la correction ne prouve rien. Cela m'a
> servi : j'avais un jour rendu des tests indépendants d'un service externe, et j'ai dû vérifier
> que la doublure n'avait pas supprimé leur pouvoir de détection.

---

## Slide 10 — C13 : la chaîne de livraison, exécutée · 1 min 30

**Sur la slide** — capture `reports/captures/04-ci-github-verte.png`
```yaml
- run: uv run python scripts/make_sample_fixture.py
- run: uv run python scripts/import_postgres.py     # PostgreSQL éphémère
- run: uv run python -m concorde.collect
- run: uv run python -m concorde.clean
- run: uv run python -m concorde.model.entrainement  # entraînement rejoué
- run: uv run pytest -m "not local_service"
- run: uv run ruff check src api app tests scripts
- run: uv run bandit  -c pyproject.toml -r src api app --severity-level medium
- run: uv run pip-audit --ignore-vuln PYSEC-2026-2447
- run: uv run python scripts/conformite.py           # ⛔ porte bloquante
- run: uv build                                       # n'est atteint que si tout précède est vert
```

**Script**
> La chaîne de livraison n'est pas un fichier YAML décoratif : elle s'exécute à chaque poussée, sur
> Ubuntu, avec Java 17 et un PostgreSQL éphémère.
>
> Elle rejoue **tout** : la génération des fixtures, l'import en base, la collecte, le nettoyage,
> et surtout l'entraînement du modèle. Puis les tests, le lint, l'analyse statique de sécurité,
> l'audit des dépendances, la porte de conformité, et enfin la construction du paquet.
>
> L'ordre est important : `uv build` est la **dernière** étape. Rien n'est construit si quelque
> chose en amont échoue. Et l'artefact publié contient la roue, l'archive source, le modèle gelé,
> sa fiche et ses métriques.
>
> Je peux vous donner le lien : cette exécution est publique et consultable.

---

## Slide 11 — C13 : la porte de conformité · 1 min 30

**Sur la slide** — extrait de `reports/annexes/conformite.md`
> **12 critères bloquants · 3 axes · verdict calculé, pas rédigé**

| ID | Axe | Seuil | Mesuré |
|---|---|---|---|
| `qualite.couverture_tests` | qualité | suite verte, couverture ≥ 75 % | **86 %** |
| `qualite.auc_autoencodeur` | qualité | AUC ≥ 0,80 | **0,9095** |
| `qualite.chaine_entrainement` | qualité | la chaîne se **rejoue** sans erreur | chaîne rejouée |
| `robustesse.perturbation` | robustesse | ≤ 10 % de bascules, bruit 1 % | 12 tests réussis |
| `securite.bandit` | sécurité | 0 HIGH, 0 MEDIUM | 0 |
| `securite.pip_audit` | sécurité | 0 vulnérabilité non acceptée | 0 |
| `securite.401_sans_cle` | sécurité | `/predict` sans clé → 401 | HTTP 401 |

> `python scripts/conformite.py` → **code de sortie 1** si un critère bloquant échoue.

**Script**
> C'est la pièce dont je suis le plus satisfait, parce qu'elle transforme « j'ai des tests » en
> « j'ai une chaîne qui décide ».
>
> Douze critères sur trois axes — qualité, robustesse, sécurité. Chacun porte son seuil, sa valeur
> mesurée, son verdict et **la justification du seuil**. Le tableau est généré, jamais rédigé à la
> main. Et le script sort en code non nul si un critère bloquant échoue, ce qui empêche la
> construction du paquet.
>
> Un critère mérite une explication : `qualite.chaine_entrainement`. Il **rejoue** l'entraînement
> complet, journalisation comprise. Je l'ai ajouté après un incident précis : la porte inspectait
> l'artefact — présent, chargeable, contrat conforme — et affichait « conforme » alors que la chaîne
> qui produit cet artefact était cassée. Un artefact valide sur le disque ne prouve que le passé.
> Il fallait que la porte prouve le présent.

---

## Slide 12 — Transition vers la démonstration · 30 s

**Sur la slide**
> **Démonstration — cinq cas réels, extraits de la table produite par la chaîne**
> Aucun cas n'est inventé pour l'occasion.

**Script**
> Je passe à la démonstration. Les cas que je vais montrer sont sélectionnés dans la table produite
> par la chaîne que je viens de décrire, par des filtres déterministes : aucun n'est inventé pour
> l'occasion. Je vais en montrer trois, qui illustrent trois comportements différents du système.

---

## DÉMONSTRATION · 5 minutes

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

## Slide 13 — Récapitulatif E3 · 45 s

**Sur la slide**

| | Preuve | Où |
|---|---|---|
| **C9** | `/predict` : auth par rôle, validation stricte, OpenAPI, 3 axes séparés | `api/model/` |
| **C10** | **Deux clients HTTP indépendants**, dégradation propre testée | `app/`, `app/web/` |
| **C11** | Evidently, latence p50/p95, taux d'erreur, seuils et alertes | `monitoring/model/` |
| **C12** | **54 tests, 86 %**, dont robustesse ; non-régression vérifiée dans les deux sens | `pytest` |
| **C13** | Chaîne CI complète exécutée + **porte de conformité bloquante** | run public + `scripts/conformite.py` |

**Script**
> Pour résumer : une API authentifiée qui expose trois axes séparés et refuse les entrées
> douteuses ; deux clients indépendants qui la consomment vraiment ; un monitoring de dérive, de
> latence et d'erreurs avec des seuils ; cinquante-quatre tests dont la robustesse du modèle ; et
> une chaîne de livraison qui s'exécute réellement et qui refuse de construire si un critère de
> conformité échoue.
>
> Je passe à l'application elle-même.

---

## Aide-mémoire — à faire AVANT la connexion au jury

```bash
source scripts/spark-env.sh
docker compose up -d                                   # PostgreSQL « healthy »
export PATH="$HOME/.lmstudio/bin:$PATH" && lms server start
lms load google/gemma-4-e4b --ttl 3600 -y              # évite le démarrage à froid

.venv/bin/uvicorn api.data.main:app  --host 127.0.0.1 --port 8001 &
.venv/bin/uvicorn api.model.main:app --host 127.0.0.1 --port 8002 &
.venv/bin/uvicorn app.main:app       --host 127.0.0.1 --port 8000 &
cd app/web && bun run build && bun run start           # :3000

# VÉRIFIER les quatre avant de partager l'écran
curl -s http://127.0.0.1:8001/sante && curl -s http://127.0.0.1:8002/sante
curl -so /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/
curl -so /dev/null -w "%{http_code}\n" http://127.0.0.1:3000/
```

**Si un service ne répond pas pendant la démo**
> Ne pas déboguer devant le jury. Basculer sur l'application Jinja (`:8000`), qui expose le même
> parcours. Si l'API modèle est tombée : **c'est une démonstration en soi** — montrer la page de
> dégradation et dire que c'est le comportement conçu et testé.

**Questions probables**
- *Pourquoi un auto-encodeur ?* → aucune étiquette n'existe, problème non supervisé ; et l'erreur se décompose par variable.
- *D'où sort le seuil de 20 % sur les surfaces ?* → surface réelle bâtie et surface habitable ne mesurent pas la même chose ; un écart modéré est attendu, au-delà c'est plus probablement deux logements.
- *Vos métriques sont-elles fiables ?* → l'AUC oui, il n'a vu ni règles ni étiquettes ; le rappel des règles est circulaire et je ne le présente pas comme une performance.
- *Pourquoi pas de GPU ?* → 8 variables, 500 lignes : le lancement des noyaux coûterait plus que le calcul, et le CPU permet à la CI de réentraîner à l'identique.
