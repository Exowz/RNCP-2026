# E1 — Collecte, stockage et mise à disposition des données

**Compétences C1 à C5 · 15 minutes · première épreuve du passage**

Chaque slide porte en bandeau discret : `Compétences prouvées : Cx`.
Le script est écrit pour être lu. Rythme visé : environ 130 mots par minute.

---

## Slide 1 — Titre et sommaire · 30 s

**Sur la slide**
> # Concorde
> ### Fiabilité des rapprochements DVF+ × DPE × Géorisques
> **E1 — Collecte, stockage et mise à disposition des données**
>
> 1. Le problème et les sources · 2. Collecte automatisée (C1) · 3. Requêtes SQL et big data (C2)
> 4. Nettoyage et agrégation (C3) · 5. Base de données et RGPD (C4) · 6. API de mise à disposition (C5)

**Script**
> Bonjour. Je vais vous présenter Concorde, et plus précisément la couche de données du projet :
> comment je collecte, comment je nettoie, comment je stocke et comment je mets à disposition.
> Je suivrai six points, dans l'ordre de la chaîne : le problème et les sources, la collecte
> automatisée, les requêtes SQL, le nettoyage, la base de données et le RGPD, puis l'API.
> Chaque affirmation que je fais est adossée à un fichier du dépôt, à une commande reproductible
> ou à un résultat que je peux vous montrer.

---

## Slide 2 — Le problème · 1 min 15

**Sur la slide** — un schéma simple : trois cylindres (DVF+, DPE, Géorisques) et un point d'interrogation entre les deux premiers.
Capture possible : `reports/captures/12-web-accueil-atlas-schema-dvf-dpe.jpg`

> **Deux bases publiques décrivent le même logement sans partager d'identifiant fiable.**
> Quand on les croise, le rapprochement peut être faux — et rien ne vous le signale.
>
> — DVF+ : les ventes immobilières déjà conclues (DGALN / Cerema)
> — DPE : les diagnostics de performance énergétique (ADEME)
> — Géorisques : l'exposition aux aléas naturels (BRGM)

**Script**
> Le point de départ est un problème concret. L'État publie trois jeux de données sur le logement.
> DVF+, qui recense les ventes immobilières déjà conclues, issues des actes notariés. Les DPE de
> l'ADEME, les diagnostics de performance énergétique, avec leur étiquette de A à G. Et Géorisques,
> qui décrit l'exposition aux aléas naturels.
>
> Ces trois bases décrivent le même parc, mais elles ne partagent aucun identifiant commun fiable.
> Si vous voulez savoir dans quel état énergétique un bien s'est vendu, vous devez rapprocher une
> vente et un diagnostic. Et ce rapprochement peut être faux — sans que rien ne vous l'indique.
>
> C'est le problème que traite Concorde. Le projet ne prédit aucun prix et ne produit aucune
> tarification : il qualifie la fiabilité d'un rapprochement. Toute la couche de données que je
> vais vous présenter est construite pour ça.

---

## Slide 3 — La chaîne du bloc 1 · 45 s

**Sur la slide** — le flux, avec les volumes réels :

> `5 types de sources` → `data/raw/ + manifeste` → `nettoyage (10 règles)` → `rapprochement` → `PostgreSQL` → `API REST`
>
> **1 743 lignes brutes → 922 rapprochements candidats → 716 appariés · 206 non évaluables**

**Script**
> Voici la chaîne complète, avec les volumes réels de la dernière exécution. Cinq types de sources
> alimentent un dossier de données brutes, accompagné d'un manifeste. Dix règles de nettoyage
> produisent un jeu propre. Le rapprochement génère 922 candidats, dont 716 sont appariés à un
> diagnostic. Et 206 ne le sont pas : je les conserve, parce que l'absence d'information est une
> information. J'y reviendrai, c'est un choix de conception central.

---

## Slide 4 — C1 : un contrat unique pour cinq types de sources · 1 min 30

**Sur la slide** — extrait de code, `src/concorde/collect/base.py` :

```python
class Collecteur(ABC):
    """Contrat d'une source de donnees.

    Les sous-classes declarent `nom`, `type_source`, `origine` et implementent
    `_collecter()`, qui renvoie un DataFrame. Tout le reste est mutualise.
    """

    nom: str
    type_source: TypeSource
    origine: str

    @abstractmethod
    def _collecter(self) -> pd.DataFrame:
        """Recupere les donnees brutes. Peut lever : l'appelant gere."""
```

**Script**
> Le référentiel demande d'automatiser l'extraction depuis cinq types de sources différents : un
> fichier, un service web, une page web, une base de données et un système big data.
>
> Le premier réflexe serait d'écrire cinq scripts indépendants. J'ai fait l'inverse : une classe
> abstraite définit le contrat, et chaque source n'implémente qu'une seule méthode, `_collecter`,
> qui renvoie un tableau de données.
>
> Tout le reste est mutualisé : le point d'entrée, la journalisation, la gestion d'erreur,
> l'écriture sur disque et l'inscription au manifeste. Concrètement, ajouter une sixième source
> coûte une vingtaine de lignes, et elle hérite automatiquement de toutes les garanties des cinq
> autres. C'est ce qui rend la chaîne homogène plutôt que d'être cinq scripts qui se ressemblent
> vaguement.

---

## Slide 5 — C1 : les cinq types, prouvés par le manifeste · 1 min 30

**Sur la slide** — le manifeste réel :

| Type exigé | Source | Lignes | Empreinte SHA-256 |
|---|---|---:|---|
| `fichier` | DVF+ (Cerema) | 997 | `49c2c76281…` |
| `big_data` | DPE via **Spark** | 726 | `24b863d225…` |
| `service_web` | Base Adresse Nationale | 3 | `0cc3efd8e0…` |
| `page_web` | Géorisques (scraping ciblé) | 2 | `47e64f251b…` |
| `base_de_donnees` | PostgreSQL | 3 | `2829767f3a…` |
| `fichier` | Géorisques (extrait figé) | 12 | `a54fa726e6…` |

> **6 collecteurs · 5 types distincts · 1 743 lignes · `data/raw/_manifest.json`**

**Script**
> Et voici la preuve. À chaque collecte, le socle écrit une entrée dans un manifeste : le type de
> source, l'origine, le nombre de lignes, la taille, la durée, l'horodatage, et une empreinte
> SHA-256 du fichier produit.
>
> Ce manifeste n'est pas de la documentation, c'est un artefact généré. Il me permet de prouver
> trois choses d'un coup. Un : les cinq types exigés sont bien présents, et je peux vous les
> montrer ligne par ligne. Deux : les volumes sont réels. Trois : l'empreinte permet de vérifier
> qu'un fichier n'a pas changé entre deux exécutions — c'est ce qui rend la chaîne reproductible
> et vérifiable.
>
> La commande est `python -m concorde.collect`, et elle régénère tout ceci en quelques secondes.

---

## Slide 6 — C1 : une source en panne n'arrête pas les autres · 1 min

**Sur la slide** — extrait de code, `src/concorde/collect/base.py` :

```python
try:
    df = self._collecter()
    ...
except Exception as exc:  # une source en panne ne doit pas tout arreter
    resultat = ResultatCollecte(..., succes=False,
                                erreur=f"{type(exc).__name__}: {exc}")
    self.log.error(f"Echec de collecte : {resultat.erreur}", exc_info=True)
enregistrer_manifeste(resultat)
```

Et une entrée réelle d'échec, capturée pendant les tests :

```json
"erreur": "ColonnesManquantes: DVF+ : colonnes obligatoires absentes
           ['valeur_fonciere', 'code_commune', ...]",
"succes": false
```

**Script**
> Le référentiel demande une gestion d'erreur. J'ai fait un choix précis : une source qui échoue
> ne remonte pas son exception jusqu'à interrompre le programme. Elle est journalisée, inscrite au
> manifeste comme échec, et la collecte continue avec les autres sources.
>
> La raison est opérationnelle : si l'API de la Base Adresse Nationale est indisponible un matin,
> je veux quand même récupérer mes quatre autres sources, et je veux savoir exactement laquelle a
> échoué et pourquoi.
>
> L'exemple que vous voyez est réel : il vient d'une exécution où le schéma du fichier DVF n'était
> pas celui attendu. Le message nomme les colonnes manquantes. Détecter ça au moment de la collecte
> coûte une seconde ; le détecter après le nettoyage coûte une heure de recherche.

---

## Slide 7 — C2 : requête SQL sur le SGBD · 1 min 30

**Sur la slide** — extrait, `docs/queries.md` :

```sql
SELECT c.code_commune, c.nom_commune,
       COALESCE(MAX(a.niveau), 0) AS alea_max,
       COUNT(*) FILTER (WHERE a.niveau >= 3) AS nb_aleas_significatifs
FROM reference_commune AS c
LEFT JOIN exposition_alea AS a USING (code_commune)
WHERE c.departement = $1
GROUP BY c.code_commune, c.nom_commune
ORDER BY c.code_commune;
```

**Script**
> Le référentiel demande des requêtes SQL documentées, avec leurs jointures, leurs filtres et
> leurs optimisations. En voici une, sur PostgreSQL.
>
> Trois choix méritent une explication. Le `LEFT JOIN` d'abord : je veux conserver les communes
> qui n'ont aucun aléa recensé. Un `INNER JOIN` les ferait disparaître silencieusement, et je me
> retrouverais à croire qu'une commune sans aléa n'existe pas. Le `COALESCE` ensuite, qui traduit
> cette absence en zéro plutôt qu'en valeur nulle, pour que le code appelant n'ait pas à gérer
> deux cas. Et le filtre `FILTER (WHERE a.niveau >= 3)`, qui compte les aléas significatifs en un
> seul passage plutôt qu'en deux requêtes.
>
> Le paramètre est passé en valeur liée, jamais concaténé dans la chaîne : c'est ce qui empêche
> l'injection SQL. La requête est testée dans `tests/data/test_requetes_sql.py`.

---

## Slide 8 — C2 : requête sur le système big data · 1 min 30

**Sur la slide** — extrait, `docs/queries.md`, et le pourquoi de Spark :

```sql
SELECT `Code_INSEE_(BAN)` AS code_commune,
       COUNT(*) AS nb_dpe,
       ROUND(AVG(CAST(`Conso_5_usages_par_m²_é_primaire` AS DOUBLE)), 2) AS conso_moyenne
FROM dpe
WHERE `Code_INSEE_(BAN)` IS NOT NULL
GROUP BY `Code_INSEE_(BAN)`
ORDER BY code_commune;
```

```python
spark = (SparkSession.builder
         .config("spark.sql.shuffle.partitions", "1")   # démo locale : une partition suffit
         .getOrCreate())
```

**Script**
> Le référentiel exige aussi une requête sur un système big data, et c'est là que Spark intervient.
>
> Je veux être précis sur la justification, parce que c'est une question que vous pourriez me poser.
> Sur mon extrait de démonstration, 726 lignes, Spark n'apporte rien : pandas serait plus rapide.
> Le choix se justifie par la cible. La base DPE de l'ADEME dépasse les dix millions
> d'enregistrements. À cette échelle, le traitement ne tient plus en mémoire sur une machine, et
> l'agrégation par commune doit être distribuée. J'ai donc écrit la chaîne avec l'outil de la
> cible, pas avec l'outil du prototype.
>
> J'ai réduit le nombre de partitions à une seule pour la démonstration, afin que la session reste
> légère et rapide. Et la session est explicitement arrêtée après la lecture, pour ne pas laisser
> une machine virtuelle Java tourner en arrière-plan.

---

## Slide 9 — C3 : des règles nommées, comptées et justifiées · 1 min 30

**Sur la slide** — extrait, `src/concorde/clean/rapprochement.py` :

```python
Regle(
    "DVF-01", "surface batie exploitable",
    "Une surface nulle, absente ou negative rend tout ratio au m2 indefini : "
    "la ligne ne peut ni etre comparee ni etre rapprochee.",
    lambda d: d[d["surface_reelle_bati"].notna() & (d["surface_reelle_bati"] > 0)],
),
```

> **Chaque règle porte : un identifiant · un libellé · une justification métier · le filtre appliqué.**

**Script**
> Le nettoyage, maintenant. Le référentiel demande des règles écrites, la suppression des entrées
> corrompues et un tableau avant-après.
>
> J'aurais pu enchaîner des filtres pandas les uns après les autres. Le problème, c'est qu'au bout
> de dix filtres, plus personne ne sait lequel a supprimé quoi, ni pourquoi.
>
> J'ai donc fait de chaque règle un objet. Elle porte un identifiant, un libellé, une justification
> métier rédigée, et le filtre lui-même. Le moteur les exécute dans l'ordre et compte, pour chacune,
> les lignes entrantes et sortantes.
>
> La conséquence pratique est importante : le tableau que je vais vous montrer est **généré**. Il
> ne peut pas diverger du code, parce qu'il est produit par le code.

---

## Slide 10 — C3 : le tableau avant / après · 1 min 30

**Sur la slide** — le résultat réel :

| Règle | Avant | Après | Supprimées |
|---|---:|---:|---:|
| `DVF-01` surface bâtie exploitable | 997 | 975 | **22** |
| `DVF-02` surface plausible (≤ 2000 m²) | 975 | 967 | **8** |
| `DVF-03` valeur foncière renseignée | 967 | 947 | **20** |
| `DVF-04` type de local retenu | 947 | 922 | **25** |
| `DVF-05` déduplication des dispositions | 922 | 904 | **18** |
| `DVF-06` date de mutation valide | 904 | 900 | **4** |

> **DVF : 997 → 900 (−9,7 %) · DPE : 726 → 689 (−5,1 %)**
> Généré par `python -m concorde.clean` → `reports/annexes/nettoyage_avant_apres.md`

**Script**
> Voici ce tableau. Chaque ligne est une règle, et chaque règle supprime des lignes réelles.
>
> Je veux insister sur un point, parce qu'il est facile à rater. Ce ne sont pas des règles
> décoratives écrites pour cocher une case : elles agissent. La règle 4, par exemple, retire vingt-cinq
> dépendances et locaux commerciaux. Pourquoi ? Parce qu'un garage n'a pas de diagnostic énergétique
> de logement comparable : le rapprocher produirait du bruit, pas de l'information.
>
> La règle 5 supprime dix-huit doublons. Dans DVF, une mutation portant plusieurs dispositions
> apparaît plusieurs fois. Sans déduplication, le même bien pèserait plusieurs fois dans mes
> statistiques.
>
> Au total, je retire près de dix pour cent des lignes DVF, et je peux justifier chaque
> suppression individuellement.

---

## Slide 11 — C3 : ce que le rapprochement ne sait pas · 1 min

**Sur la slide**

> **922 rapprochements candidats**
> — **716** appariés à un diagnostic
> — **206** sans DPE → conservés, jamais scorés
> — **44** parcelles portant plusieurs DPE → ambiguïté mesurée, pas masquée

**Script**
> Le rapprochement se fait sur la parcelle cadastrale, seul identifiant partagé entre DVF et
> l'adressage des DPE. Ce choix est discutable, et c'est justement le sujet du projet.
>
> Il est fiable quand une parcelle porte un seul logement. Il devient ambigu dès qu'elle en porte
> plusieurs — en copropriété, typiquement. Quarante-quatre parcelles sont dans ce cas chez moi.
> Je ne masque pas cette ambiguïté : je la compte, je la stocke dans une colonne, et elle fera
> baisser le niveau de confiance en aval.
>
> Et deux cent six mutations n'ont aucun diagnostic rapprochable. Je les conserve. J'aurais pu les
> supprimer pour avoir un jeu plus propre — j'ai fait l'inverse, parce que l'absence d'information
> est une information, et que le produit doit pouvoir répondre « je ne sais pas ».

---

## Slide 12 — C4 : le modèle de données · 1 min

**Sur la slide** — le MCD/MPD, depuis `docs/data-model.md`, et :

> **PostgreSQL 17**, conteneurisé · port 5433
> `reference_commune` · `exposition_alea`
> Import **idempotent** : `python scripts/import_postgres.py`

**Script**
> Pour le stockage, j'ai retenu PostgreSQL, en conteneur Docker. Deux raisons : c'est un SGBD
> relationnel complet, qui me permet de démontrer de vraies jointures ; et le conteneur rend
> l'installation reproductible sur n'importe quelle machine, ce qui compte pour une démonstration.
>
> Le modèle conceptuel et le modèle physique sont documentés dans le dépôt. Le script d'import est
> idempotent : je peux le relancer autant de fois que je veux, il ne crée pas de doublons. C'est ce
> qui permet de rejouer la chaîne complète sans repartir d'une base vierge.

---

## Slide 13 — C4 : le RGPD, vérifié et non déclaré · 1 min 30

**Sur la slide** — extrait, `tests/api/test_api_data.py` :

```python
@pytest.mark.regression
def test_aucune_adresse_detaillee_n_est_publiee_par_l_api_data() -> None:
    """Verrouille l'engagement de minimisation du registre RGPD. (C4, C17)"""
    for reponse in reponses:
        assert "adresse_ban" not in reponse.text, (
            "Une adresse est exposee : cela contredit docs/rgpd.md."
        )
```

**Script**
> Le RGPD, maintenant, et je voudrais vous montrer une chose dont je suis assez satisfait.
>
> J'ai un registre RGPD classique : finalité, base légale, minimisation, conservation, sécurité.
> Il engage notamment Concorde à ne publier aucune adresse détaillée dans l'API, parce que croiser
> une adresse précise, un prix de vente et une étiquette énergétique permet de désigner un logement,
> donc potentiellement son occupant.
>
> Le problème, c'est qu'un registre RGPD est un document. Rien n'empêche le code de s'en écarter.
> C'est d'ailleurs exactement ce qui m'est arrivé : en ajoutant des routes à l'API, j'ai exposé
> sans le vouloir le champ adresse. Le registre disait une chose, le code en faisait une autre.
>
> J'ai corrigé, et surtout j'ai écrit ce test. Il interroge les trois routes exposées et échoue si
> une adresse réapparaît, y compris par inadvertance. L'engagement n'est plus une intention : c'est
> une contrainte vérifiée à chaque exécution.

---

## Slide 14 — C5 : l'API de mise à disposition · 1 min 30

**Sur la slide** — extrait, `api/data/main.py` :

```python
@app.get("/communes", tags=["donnees"])
def communes(
    departement: Annotated[str, Query(pattern=r"^[0-9]{2}$", examples=["33"])],
    identite: Annotated[Identite, Depends(exige_role("reader"))],
) -> list[dict]:
    """Liste les communes d'un departement et leur synthese d'aleas."""
```

> Routes : `/communes` · `/rapprochements` · `/rapprochements/{id}` · `/rapprochements/demonstration` · `/sante`
> **Authentification par clé et par rôle · OpenAPI générée · sans clé → 401**

**Script**
> Dernier point du bloc : la mise à disposition. L'API expose les données par cinq routes REST.
>
> Trois éléments sur cette signature. Le paramètre `departement` est contraint par une expression
> régulière : deux chiffres, rien d'autre. Une entrée non conforme est rejetée avant d'atteindre
> le code métier, avec un message qui nomme le champ fautif.
>
> La dépendance `exige_role("reader")` impose une clé d'API valide et un rôle suffisant. Sans clé,
> la route répond 401 — je peux vous le montrer en direct si vous le souhaitez.
>
> Et la documentation OpenAPI est générée à partir de ces annotations. Elle décrit donc le contrat
> réellement appliqué, pas un contrat rédigé à côté qui pourrait dériver.

---

## Slide 15 — Récapitulatif E1 · 30 s

**Sur la slide**

| | Preuve | Où |
|---|---|---|
| **C1** | 5 types de sources, manifeste SHA-256, gestion d'erreur | `python -m concorde.collect` |
| **C2** | Jointure PostgreSQL + agrégation Spark SQL, testées | `docs/queries.md` |
| **C3** | 10 règles comptées, tableau généré, 922 rapprochements | `python -m concorde.clean` |
| **C4** | MCD/MPD, PostgreSQL 17, import idempotent, RGPD **testé** | `docs/rgpd.md` |
| **C5** | 5 routes REST, auth par rôle, OpenAPI | `api/data/` |

**Script**
> Pour résumer : cinq types de sources prouvés par un manifeste, des requêtes SQL et Spark
> documentées et testées, dix règles de nettoyage dont l'effet est mesuré, une base PostgreSQL avec
> son modèle et un registre RGPD vérifié par un test, et une API authentifiée et documentée.
>
> Tout est reproductible par trois commandes, et je peux exécuter n'importe laquelle devant vous.
> Je passe à la présentation du modèle et de sa mise en service.

---

## Aide-mémoire — avant de commencer

```bash
source scripts/spark-env.sh
docker compose up -d                      # PostgreSQL doit être « healthy »
python -m concorde.collect                # doit afficher 6/6 sources
```

**Si on te demande de montrer quelque chose en direct**
- le manifeste : `cat data/raw/_manifest.json`
- le tableau avant/après : `cat reports/annexes/nettoyage_avant_apres.md`
- le refus sans clé : `curl -i http://127.0.0.1:8001/communes?departement=33` → 401
- la doc de l'API : `http://127.0.0.1:8001/docs`
