# Incident CI-2026-08-24 — chaine de verification indisponible

## Contexte et impact

La verification GitHub Actions est la porte d'entree de livraison de Concorde.
Le 24 aout, deux executions consecutives ont echoue alors que la chaine locale
semblait verte. L'impact etait concret : aucun artefact ne pouvait etre livre
avec une preuve d'integration continue reproductible.

Les executions et leurs logs restent consultables publiquement :

| Execution | Commit | Symptôme observable |
|---|---|---|
| [32772167461](https://github.com/Exowz/RNCP-2026/actions/runs/32772167461) | `20ddf4c` | `UndefinedTable: relation "reference_commune" does not exist` pendant la collecte. |
| [32772345019](https://github.com/Exowz/RNCP-2026/actions/runs/32772345019) | `daa9399` | `ModuleNotFoundError: No module named 'api'` et `app` pendant la collecte des tests. |

## Reproduction et diagnostic

La premiere erreur se reproduisait a chaque CI : le collecteur PostgreSQL
lisait `reference_commune` avant l'execution du script qui cree et peuple cette
table. Le diagnostic a compare l'ordre des etapes du workflow avec la
dependance explicite du collecteur. La cause est donc un ordre d'initialisation
invalide, pas une indisponibilite de PostgreSQL.

Apres correction de cet ordre, la seconde CI a fait passer la collecte, le
nettoyage et l'entrainement puis a echoue lors de `uv run pytest`. La meme
commande, lancee localement, reproduisait exactement les quatre erreurs
d'import. Le paquet Hatch ne declarait que `src/concorde` : lors de
l'installation editable par UV, les paquets racine `api` et `app` n'etaient pas
exposes a pytest. La difference avec le lancement direct de `.venv/bin/pytest`
venait donc du mode d'installation, pas du code des endpoints.

## Correctifs minimaux

1. Commit [`daa9399`](https://github.com/Exowz/RNCP-2026/commit/daa9399) :
   execution de `scripts/import_postgres.py` avant `python -m concorde.collect`.
2. Commit [`23c5421`](https://github.com/Exowz/RNCP-2026/commit/23c5421) :
   declaration de `api` et `app` dans les paquets de la roue Hatch.

Ces modifications corrigent la cause a la source ; aucun test n'est ignore ni
marque comme optionnel. Le marqueur `local_service` demeure exclu de la CI par
conception : il depend du serveur LM Studio deja charge sur le poste de
demonstration, qui ne doit ni etre telecharge ni simule par GitHub.

## Non-regression et retour d'experience

La commande de reproduction automatisee est :

```bash
source scripts/spark-env.sh
uv run pytest -m "not local_service"
```

Elle passe localement : `13 passed, 1 deselected`. La
[troisieme execution 32772913151](https://github.com/Exowz/RNCP-2026/actions/runs/32772913151),
declenchee sur `23c5421`, passe egalement toutes les etapes : fixture,
import PostgreSQL, collecte Spark, nettoyage, entrainement, tests et lint.
Cette execution est le test de non-regression d'integration : elle couvre
l'ordre du workflow et le packaging editable, deux elements invisibles dans un
test unitaire isole.

**REX.** Un lancement local direct peut masquer une erreur de packaging car le
repertoire de travail est accessible dans `sys.path`. La commande de reference
est desormais `uv run ...`, identique a celle de la CI. Toute evolution de la
chaine doit etre verifiee avec Java 17 et le workflow distant avant livraison.

---

# Incident APP-2026-08-25 — la bascule de profil renvoyait `405` en pleine demonstration

## Contexte et impact

Le parcours de demonstration repose sur une bascule : le **meme** rapprochement,
lu en profil « particulier » puis en profil « analyste credit ». C'est la
demonstration centrale du produit — le calcul ne change pas, seule la
restitution change.

Depuis la page de resultat, un clic sur « Analyste crédit » affichait
`{"detail":"Method Not Allowed"}` en JSON brut. Impact : le parcours casse
exactement a l'etape qui doit convaincre, et sur un ecran technique illisible
pour un utilisateur.

## Reproduction

Deterministe, en deux gestes :

```bash
.venv/bin/uvicorn app.main:app --port 8000    # + API modele sur 8002
# Ouvrir /, choisir un cas, « Evaluer », puis cliquer « Analyste crédit »
```

Ou directement : `curl -i "http://127.0.0.1:8000/evaluer?profil=analyste"` →
`HTTP/1.1 405 Method Not Allowed`.

## Diagnostic

Dans `app/templates/base.html`, les liens de profil du bandeau etaient
relatifs : `href="?profil={{ cle }}"`. Un lien relatif de cette forme conserve
le chemin courant et emet un **GET**. Sur `/`, `/transparence` et
`/exploitation` — toutes des routes GET — le lien fonctionnait. Sur `/evaluer`,
declaree en **POST** uniquement parce qu'elle repondait a un formulaire, le GET
n'avait aucun gestionnaire : Starlette repondait `405`.

La cause n'est donc ni le modele ni l'API : c'est une **hypothese implicite du
gabarit** — « toute page est atteignable en GET » — qui n'etait vraie que pour
trois pages sur quatre. Le defaut etait invisible en test unitaire parce
qu'aucun test ne suivait les liens du bandeau.

## Correctif

1. `app/main.py` : ajout d'un gestionnaire `GET /evaluer` partageant la meme
   fonction de rendu que le POST. L'evaluation est idempotente et sans effet de
   bord (lecture d'une fixture + appel a l'API modele) : l'exposer en GET est
   legitime, et rend le resultat partageable par URL.
2. `app/main.py` : les liens de profil sont desormais **construits cote
   serveur** (`_liens_profil`), en conservant le chemin et les parametres utiles
   — dont `cas` — et en ne remplacant que `profil`. Le gabarit ne fabrique plus
   d'URL.

## Non-regression

`tests/app/test_bascule_profil.py`, six tests portant le marqueur `regression` :

- `GET /evaluer` doit rendre du HTML et non `405` ;
- le lien de profil doit conserver le cas evalue ;
- la bascule doit rester disponible sur les quatre pages (parametre) ;
- les deux profils doivent restituer **le meme calcul**, seule la profondeur
  technique differant.

**Preuve avant/apres.** Correctif retire (`git stash`), les six tests echouent,
le journal enregistrant `GET /evaluer -> 405`. Correctif remis, les six passent.

## REX

Un lien relatif porte une hypothese sur le verbe HTTP de la page courante. Des
qu'une route repond a un formulaire, cette hypothese devient fausse sans que
rien ne le signale. Regle retenue : **aucune URL n'est fabriquee dans un
gabarit** ; elles sont construites cote serveur, ou le jeu de routes est connu.
Un test de parcours suivant les liens de navigation aurait attrape le defaut
avant la demonstration — c'est desormais le cas.

---

# Incident CI-2026-08-25 — des tests verts en local, rouges en integration continue

## Contexte et impact

Les six tests de non-regression ecrits pour l'incident `APP-2026-08-25`
passaient sur le poste de developpement et faisaient echouer la CI. Impact
direct : la chaine de livraison etait bloquee, et la preuve C18 — une execution
verte — perdue, alors que le code applicatif etait correct.

Le symptome ecartait d'emblee l'hypothese d'une regression du correctif : les
tests echouaient en `503 Service Unavailable`, pas en `405 Method Not Allowed`.
Ce n'etait donc pas le bug d'origine qui reapparaissait.

| Execution | Commit | Symptome |
|---|---|---|
| [32850513335](https://github.com/Exowz/RNCP-2026/actions/runs/32850513335) | `6a2ac96` | `4 failed, 30 passed` — `assert 503 == 200` |

## Diagnostic

`503` est le code que l'application Jinja renvoie lorsqu'elle ne parvient pas a
joindre l'API modele. Les tests instanciaient l'application, qui appelle son
amont en HTTP sur `127.0.0.1:8002`.

Cette API tourne en permanence sur le poste de developpement, jamais sur un
runner GitHub. Les tests portaient donc une **dependance d'environnement
implicite** : ils ne verifiaient pas seulement le routage, ils exigeaient un
service tiers demarre. Le poste de developpement masquait la dependance
exactement comme il avait masque, la veille, une erreur de packaging.

La cause n'est ni le code applicatif ni la CI : c'est le **perimetre des tests**,
plus large que leur intention.

## Correctif

Une fixture `autouse` remplace le transport HTTP par un appel direct au moteur.
Le **vrai moteur** est conserve — seul le saut reseau est retire — parce que ces
tests portent sur le routage et le rendu, pas sur le transport.

L'appel HTTP reel n'est pas pour autant sans preuve : il reste couvert par la
sonde `/sante` de l'application, qui interroge son amont et rapporte son etat,
et par la demonstration elle-meme.

## Verification, dans les deux sens

Un test rendu hermetique peut avoir perdu son pouvoir de detection. Les deux
sens ont donc ete controles :

```bash
# 1. Condition de la CI reproduite : toutes les APIs arretees
pytest -m "not local_service"        # 34 passed

# 2. Correctif du 405 retire : les tests doivent echouer
pytest tests/app/test_bascule_profil.py   # 6 failed, "GET /evaluer -> 405" journalise
```

Execution verte confirmee :
[32850978029](https://github.com/Exowz/RNCP-2026/actions/runs/32850978029) sur
`7b0c9e7` — fixtures, PostgreSQL, collecte, nettoyage, entrainement, tests,
lint, build et artefact.

## REX

Un test qui reussit sur le poste de developpement et echoue en CI ne signale pas
un probleme de CI : il signale que le poste fournissait silencieusement quelque
chose. Deux incidents sur trois ont eu cette forme — un paquet expose par le
repertoire courant, puis un service deja demarre.

Regle retenue : **un test doit declarer ce dont il depend**. Ce qui n'est pas
l'objet du test se remplace par une doublure, et l'on verifie que la doublure
n'a pas supprime le pouvoir de detection. La CI n'est pas un obstacle a franchir,
c'est le seul environnement qui ne ment pas sur les dependances.

---

# Incident SEC-2026-08-25 — la porte de conformité détectait deux dépendances vulnérables

## Contexte et impact

Le projet de substitution n°21 revendique une validation sécurité avant
déploiement. Le 25 août, le premier passage de `scripts/conformite.py` est
rouge : `pip-audit` signale `cryptography 49.0.0` (`PYSEC-2026-3552`, correctif
50.0.0) et `diskcache 5.6.3` (`PYSEC-2026-2447`, aucun correctif listé).
L'impact est direct : un paquet aurait pu être construit alors que son graphe
de dépendances contenait au moins une vulnérabilité corrigeable.

## Reproduction et diagnostic

```bash
.venv/bin/pip-audit
# Found 2 known vulnerabilities in 2 packages
```

La porte appelait le même audit et renvoyait un code non nul. L'inspection du
graphe a établi `concorde -> dvc -> dvc-data -> diskcache`. `cryptography`
n'était pas contraint explicitement par le projet et le verrou retenait 49.0.0.
Le second avis est transitif à la brique DVC imposée et ne propose, à cette
date, aucune version de correction.

## Correctifs minimaux

1. Ajout de `cryptography>=50.0.0` dans `pyproject.toml`, puis régénération de
   `uv.lock` : l'environnement utilise désormais 50.0.0. La distribution
   complète de MLflow exigeant encore `cryptography<50`, elle est remplacée par
   `mlflow-skinny`, suffisant pour le tracking SQLite local utilisé par le code.
2. Initialisation réelle de DVC avec un remote local ; l'exception
   `PYSEC-2026-2447` est limitée à `diskcache`, datée et documentée dans
   `docs/securite.md`. Elle ne masque aucune autre vulnérabilité et sera revue
   au plus tard le 2026-09-25.
3. Ajout de Bandit, de pip-audit et de la porte avant `uv build` dans la CI.

## Non-regression et retour d'experience

```bash
.venv/bin/pip-audit --ignore-vuln PYSEC-2026-2447
.venv/bin/bandit -c pyproject.toml -r src api app
source scripts/spark-env.sh
.venv/bin/python scripts/conformite.py
```

Ces commandes ne laissent plus de vulnérabilité non acceptée, ni finding Bandit
HIGH ou MEDIUM. La vérification forcée
`python scripts/conformite.py --forcer-echec qualite.auc_autoencodeur` reste
non nulle : le vert n'est donc pas une exception silencieuse.

**REX.** Une liste de dépendances déclarée ne constitue pas un contrôle. Le
contrôle doit être exécuté, pouvoir bloquer le build et distinguer clairement
une exception assumée d'un résultat conforme. Hors ligne, pip-audit devient
« non évalué » : la démonstration continue, mais le rapport ne prétend jamais
que la sécurité a été mesurée.

---

# Incident SEC-2026-08-25-bis — la porte de conformité déclarait conforme une chaîne cassée

## Contexte et impact

C'est l'incident le plus instructif du projet, parce qu'il porte sur l'outil de
contrôle lui-même.

Pour lever le plafond `cryptography<50` imposé par la distribution complète de
MLflow — plafond qui empêchait de corriger `PYSEC-2026-3552` — `mlflow` a été
remplacé par `mlflow-skinny`. Le raisonnement était juste : le projet n'utilise
ni le serveur ni l'interface de MLflow.

Mais `mlflow-skinny` n'embarque pas les dépendances du magasin SQL. Or Concorde
journalise dans `sqlite:///mlflow.db` — MLflow 3 ayant déprécié le magasin
fichier — et applique des migrations de schéma à l'ouverture.

```
python -m concorde.model.entrainement
ModuleNotFoundError: No module named 'alembic'
code de sortie : 1
```

**La chaîne d'entraînement ne fonctionnait plus.** C'est C13, et c'est l'étape
que la CI exécute : elle serait passée au rouge.

## Ce qui rend cet incident intéressant

Trois filets de sécurité l'ont laissé passer.

1. **Les tests ne le voyaient pas.** `tests/model/test_entrainement.py`
   neutralise la journalisation :
   `monkeypatch.setattr(entrainement, "_journaliser_mlflow", lambda *args: None)`.
   Le chemin cassé n'était jamais exercé.
2. **La porte de conformité non plus** — et elle affichait « CONFORME ». Elle
   vérifiait que l'artefact existait, se chargeait et respectait son contrat de
   variables. Les trois étaient vrais : l'artefact valide était resté sur le
   disque depuis le passage précédent. **Un artefact valide ne prouve que le
   passé.**
3. **La documentation affirmait le contraire.** `docs/securite.md` écrivait que
   `mlflow-skinny` « couvre le tracking SQLite réellement utilisé par
   Concorde ». C'était précisément ce qui ne fonctionnait pas — et c'était la
   justification du remplacement.

## Correctif

1. Verrou explicite `alembic>=1.13`, déclaré comme la **contrepartie assumée**
   du passage à l'édition skinny, avec la raison en commentaire dans
   `pyproject.toml`.
2. Nouveau critère bloquant `qualite.chaine_entrainement` : il **rejoue**
   `entrainer_et_geler`, journalisation MLflow comprise, dans un répertoire
   temporaire — la porte ne doit jamais modifier l'artefact suivi par DVC.
3. Correction de l'affirmation fausse dans `docs/securite.md`.

## Non-régression, vérifiée dans les deux sens

```bash
# 1. Panne recréée à l'identique
pip uninstall -y alembic && python scripts/conformite.py
#   → NON CONFORME (12 critères), code de sortie 1
#   → critère qualite.chaine_entrainement : non conforme

# 2. Dépendance restaurée
uv sync --extra dev && python scripts/conformite.py
#   → CONFORME (12 critères), code de sortie 0
```

## REX

Un contrôle qui inspecte un **résultat** ne prouve pas que le **processus** qui
l'a produit fonctionne encore. La porte examinait un artefact ; il fallait
qu'elle rejoue la chaîne.

Corollaire sur les doublures de test : neutraliser une dépendance dans un test
est légitime — nous l'avons fait à bon droit pour le transport HTTP dans
`CI-2026-08-25` — mais chaque doublure crée une zone que plus rien ne couvre.
Elle doit être compensée ailleurs, ici par un critère de porte qui exécute pour
de vrai.

Enfin, motif récurrent, désormais rencontré quatre fois sur cinq incidents :
**la documentation affirmait ce que le code ne faisait pas.** Registre RGPD,
versionnement DVC, tracking MLflow. À chaque fois la correction a consisté à
rendre l'affirmation vraie *et* à la faire vérifier par un test ou un critère.
