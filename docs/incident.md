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

Depuis la page de resultat, un clic sur « Analyste credit » affichait
`{"detail":"Method Not Allowed"}` en JSON brut. Impact : le parcours casse
exactement a l'etape qui doit convaincre, et sur un ecran technique illisible
pour un utilisateur.

## Reproduction

Deterministe, en deux gestes :

```bash
.venv/bin/uvicorn app.main:app --port 8000    # + API modele sur 8002
# Ouvrir /, choisir un cas, « Evaluer », puis cliquer « Analyste credit »
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
