# E1 — Collecte, stockage et mise à disposition des données

**Compétences C1 à C5 · 15 minutes · première épreuve du passage**

Bandeau discret sur chaque slide : `Compétences prouvées : Cx`.
Script écrit pour être lu. Rythme visé : ~135 mots/minute.
**E1 porte l'introduction générale du projet** — les quatre autres soutenances entrent directement dans le sujet.

---

## Slide 1 — Titre · 20 s

**Sur la slide**
> # Concorde
> ### Qualifier la fiabilité d'un croisement de données publiques
> **E1 — Collecte, stockage et mise à disposition · C1 à C5**
>
> Mathew Kapoor · RNCP Développeur en intelligence artificielle · 27 août 2026

**Script**
> Bonjour. Je vais vous présenter Concorde, et cette première épreuve porte sur la couche de
> données : comment je collecte, comment je nettoie, comment je stocke, comment je mets à
> disposition. Avant d'entrer dans la technique, je voudrais expliquer le choix du sujet, parce
> qu'il commande tout ce qui suit.

---

## Slide 2 — Pourquoi ce sujet · 1 min 30

**Sur la slide**
> **Master AI & Data for Finance** — rentrée 2026
>
> Le réflexe attendu : **prédire** un prix, **scorer** un risque.
> Mon choix : **ne pas le faire.**
>
> > Un modèle de risque ne vaut jamais mieux que les données qu'on lui donne.
>
> Je traite le problème **en amont** : quand on croise des sources publiques,
> **comment sait-on que le croisement est juste ?**

**Script**
> Je suis admis en Master AI and Data for Finance pour la rentrée. Je voulais donc un projet qui
> me prépare réellement à ce secteur, et pas un exercice hors sol.
>
> Le réflexe aurait été de faire de la prédiction : estimer un prix au mètre carré, scorer un
> risque. Je ne l'ai pas fait, et c'est un choix délibéré que j'assume complètement.
>
> La raison est simple. En finance, un modèle de risque ne vaut jamais mieux que les données qu'on
> lui donne. On peut construire le meilleur modèle du monde : si ses entrées sont fausses, sa
> sortie l'est aussi, et rien ne le signale. Le problème que j'ai trouvé le plus intéressant, et
> le plus utile, est donc celui d'avant : quand on croise plusieurs sources publiques pour nourrir
> une décision, comment sait-on que le croisement est juste ?
>
> C'est le travail dont dépend tout le reste, et c'est celui qu'on saute le plus souvent. J'ai
> préféré le traiter à fond plutôt que d'ajouter une couche prédictive que je n'aurais pas pu
> valider sérieusement en trois jours.

---

## Slide 3 — Le terrain : trois bases, aucune clé commune · 1 min 15

**Sur la slide** — schéma : trois cylindres, un point d'interrogation entre DVF+ et DPE.
Capture : `reports/captures/12-web-accueil-atlas-schema-dvf-dpe.jpg`

> | Source | Publiée par | Contenu |
> |---|---|---|
> | **DVF+** | DGALN / Cerema | ventes immobilières **déjà conclues**, actes notariés |
> | **DPE** | ADEME | diagnostics énergétiques, étiquette A→G |
> | **Géorisques** | BRGM | exposition aux aléas naturels |
>
> **Aucun identifiant commun fiable.** Le rapprochement est une **hypothèse**, jamais un fait.
>
> Cas d'usage : un analyste crédit prend le logement en **garantie**. Un bien classé G subit
> interdiction de location et obligation de rénovation. Si l'étiquette vient d'un rapprochement
> faux, la garantie est mal évaluée.

**Script**
> Le terrain, c'est l'immobilier, parce qu'il réunit trois bases publiques riches et
> structurellement mal reliées.
>
> DVF+ recense les ventes déjà conclues, issues des actes notariés — attention, ce ne sont pas les
> biens en vente. Les DPE de l'ADEME donnent l'étiquette énergétique. Géorisques donne l'exposition
> aux aléas naturels.
>
> Ces trois bases décrivent le même parc et ne partagent aucun identifiant commun fiable. Quand
> vous rapprochez une vente et un diagnostic, vous formulez une hypothèse — vous ne constatez pas
> un fait. Et personne ne vous dit quand l'hypothèse est fausse.
>
> Le lien avec la finance est direct. Une banque qui accorde un prêt immobilier prend le logement
> en garantie. Un bien classé G est aujourd'hui frappé d'interdiction de location et d'obligation
> de rénovation : sa valeur de garantie change. Si l'étiquette énergétique vient d'un rapprochement
> erroné, la banque a mal évalué son collatéral, et elle ne le sait pas.
>
> Concorde ne prend pas cette décision à sa place. Il lui dit à quel point elle peut se fier à la
> donnée sur laquelle elle s'apprête à la prendre.

---

## Slide 4 — La chaîne du bloc 1, avec ses volumes · 45 s

**Sur la slide**
> `5 types de sources` → `data/raw/ + manifeste SHA-256` → `10 règles de nettoyage` → `rapprochement` → `PostgreSQL 17` → `API REST`
>
> | Étape | Volume réel |
> |---|---|
> | Collecte, 6 collecteurs | **1 743 lignes** |
> | Après nettoyage | DVF 997→**900** · DPE 726→**689** |
> | Rapprochements candidats | **922** |
> | dont appariés à un DPE | **716** |
> | dont **non évaluables**, conservés | **206** |
> | parcelles portant plusieurs DPE | **44** |
>
> Reproductible : `python -m concorde.collect && python -m concorde.clean`

**Script**
> Voici la chaîne complète, avec les volumes de la dernière exécution — ce sont des chiffres réels,
> régénérables devant vous en une trentaine de secondes.
>
> Six collecteurs couvrant cinq types de sources produisent 1 743 lignes brutes. Dix règles de
> nettoyage en retirent une partie. Le rapprochement produit 922 candidats, dont 716 sont appariés
> à un diagnostic. Deux cent six ne le sont pas, et je les conserve. Quarante-quatre parcelles
> portent plusieurs diagnostics, donc le rapprochement y est ambigu.
>
> Ces deux derniers chiffres sont le cœur du produit, j'y reviendrai.

---

## Slide 5 — C1 : un contrat unique pour cinq types de sources · 1 min 15

**Sur la slide**
```python
class Collecteur(ABC):
    """Contrat d'une source de donnees."""
    nom: str
    type_source: TypeSource        # fichier | service_web | page_web
    origine: str                   #  | base_de_donnees | big_data

    @abstractmethod
    def _collecter(self) -> pd.DataFrame:
        """Recupere les donnees brutes. Peut lever : l'appelant gere."""
```
> **Mutualisé par le socle** : point d'entrée · journalisation · gestion d'erreur · écriture · manifeste
> → une nouvelle source coûte ~20 lignes et hérite de toutes les garanties.

**Script**
> Le référentiel demande d'automatiser l'extraction depuis cinq types de sources : fichier, service
> web, page web, base de données et système big data.
>
> Le premier réflexe serait d'écrire cinq scripts. J'ai fait l'inverse : une classe abstraite
> définit le contrat, et chaque source n'implémente qu'une méthode, qui renvoie un tableau de
> données. Le socle mutualise tout le reste — le point d'entrée, la journalisation, la gestion
> d'erreur, l'écriture sur disque, l'inscription au manifeste.
>
> Concrètement, ajouter une sixième source coûte une vingtaine de lignes, et elle hérite
> automatiquement des garanties des cinq autres. C'est ce qui fait une chaîne homogène plutôt que
> cinq scripts qui se ressemblent vaguement.

---

## Slide 6 — C1 : les cinq types, prouvés par le manifeste · 1 min 30

**Sur la slide**

| Type exigé | Source | Lignes | Durée | SHA-256 |
|---|---|---:|---:|---|
| `fichier` | DVF+ (Cerema) | 997 | 0,5 s | `49c2c76281…` |
| `big_data` | DPE via **Spark** | 726 | 4,2 s | `24b863d225…` |
| `service_web` | Base Adresse Nationale | 3 | 0,00 s | `0cc3efd8e0…` |
| `page_web` | Géorisques (scraping ciblé) | 2 | 0,01 s | `47e64f251b…` |
| `base_de_donnees` | PostgreSQL | 3 | 0,01 s | `2829767f3a…` |
| `fichier` | Géorisques (extrait figé) | 12 | 0,00 s | `a54fa726e6…` |

> **6 collecteurs · 5/5 types exigés · 1 743 lignes** — `data/raw/_manifest.json`, **artefact généré**

**Script**
> Et voici la preuve. À chaque collecte, le socle écrit une entrée dans un manifeste : le type,
> l'origine, le nombre de lignes, la taille, la durée, l'horodatage, et une empreinte SHA-256 du
> fichier produit.
>
> Ce manifeste n'est pas de la documentation, c'est un artefact généré, et il prouve trois choses
> d'un coup. Les cinq types exigés sont présents, ligne par ligne. Les volumes sont réels. Et
> l'empreinte permet de vérifier qu'un fichier n'a pas changé entre deux exécutions.
>
> C'est ce qui rend la chaîne vérifiable et non pas seulement racontée. La commande est
> `python -m concorde.collect`.

---

## Slide 7 — C1 : une source en panne n'arrête pas les autres · 1 min

**Sur la slide**
```python
try:
    df = self._collecter()
except Exception as exc:  # une source en panne ne doit pas tout arreter
    resultat = ResultatCollecte(..., succes=False,
                                erreur=f"{type(exc).__name__}: {exc}")
    self.log.error(f"Echec de collecte : {resultat.erreur}", exc_info=True)
enregistrer_manifeste(resultat)   # succes OU echec : toujours trace
```
Échec réel, capturé par le manifeste :
```json
"erreur": "ColonnesManquantes: DVF+ : colonnes obligatoires absentes
           ['valeur_fonciere', 'code_commune', 'id_parcelle', ...]",
"succes": false
```

**Script**
> Le référentiel demande une gestion d'erreur. J'ai fait un choix précis : une source qui échoue
> ne remonte pas son exception jusqu'à interrompre le programme. Elle est journalisée, inscrite au
> manifeste comme échec, et la collecte continue.
>
> La raison est opérationnelle. Si l'API de la Base Adresse Nationale est indisponible un matin,
> je veux récupérer mes quatre autres sources, et savoir exactement laquelle a échoué et pourquoi.
>
> L'exemple affiché est réel. Il vient d'une exécution où le schéma du fichier DVF n'était pas
> celui attendu : le message nomme les six colonnes manquantes. Détecter ça à la collecte coûte une
> seconde ; le détecter après le nettoyage coûte une heure.

---

## Slide 8 — C2 : requête SQL sur le SGBD · 1 min 15

**Sur la slide**
```sql
SELECT c.code_commune, c.nom_commune,
       COALESCE(MAX(a.niveau), 0)                        AS alea_max,
       COUNT(*) FILTER (WHERE a.niveau >= 3)             AS nb_aleas_significatifs
FROM reference_commune AS c
LEFT JOIN exposition_alea AS a USING (code_commune)
WHERE c.departement = $1          -- valeur liée, jamais concaténée
GROUP BY c.code_commune, c.nom_commune;
```
> `LEFT JOIN` → conserve les communes **sans** aléa · `COALESCE` → l'absence devient 0
> `FILTER` → compte les aléas significatifs **en un seul passage** · `$1` → pas d'injection SQL
> Testée : `tests/data/test_requetes_sql.py`

**Script**
> Le référentiel demande des requêtes SQL documentées, avec leurs jointures, leurs filtres et
> leurs optimisations. En voici une.
>
> Quatre choix. Le `LEFT JOIN` conserve les communes sans aléa recensé : un `INNER JOIN` les ferait
> disparaître silencieusement, et je croirais qu'une commune sans aléa n'existe pas. Le `COALESCE`
> traduit cette absence en zéro, pour que le code appelant n'ait pas deux cas à gérer. Le `FILTER`
> compte les aléas significatifs dans le même passage, au lieu d'une seconde requête. Et le
> paramètre est une valeur liée, jamais concaténée : c'est ce qui empêche l'injection SQL.
>
> La requête est couverte par un test.

---

## Slide 9 — C2 : requête sur le système big data · 1 min 15

**Sur la slide**
```sql
SELECT `Code_INSEE_(BAN)` AS code_commune,
       COUNT(*)                                                    AS nb_dpe,
       ROUND(AVG(CAST(`Conso_5_usages_par_m²_é_primaire` AS DOUBLE)), 2) AS conso_moyenne
FROM dpe
WHERE `Code_INSEE_(BAN)` IS NOT NULL
GROUP BY `Code_INSEE_(BAN)`;
```
```python
spark = (SparkSession.builder
         .config("spark.sql.shuffle.partitions", "1")   # démo locale : 1 partition suffit
         .getOrCreate())
# session explicitement arrêtée après lecture : pas de JVM résiduelle
```
> **Pourquoi Spark sur 726 lignes ?** Parce que la cible, c'est la base ADEME : **> 10 M de DPE**.
> J'écris la chaîne avec l'outil de la cible, pas celui du prototype.

**Script**
> Le référentiel exige aussi une requête sur un système big data, et c'est là que Spark intervient.
>
> Je veux devancer la question, parce qu'elle est légitime : sur mon extrait de 726 lignes, Spark
> n'apporte rien. Pandas serait plus rapide. Le choix se justifie par la cible : la base DPE de
> l'ADEME dépasse dix millions d'enregistrements. À cette échelle, le traitement ne tient plus en
> mémoire sur une machine et l'agrégation doit être distribuée. J'ai donc écrit la chaîne avec
> l'outil de la cible, pas avec celui du prototype.
>
> Deux réglages pour que la démonstration reste légère : une seule partition, et la session est
> explicitement arrêtée après lecture pour ne pas laisser une machine virtuelle Java en arrière-plan.

---

## Slide 10 — C3 : des règles nommées, comptées, justifiées · 1 min

**Sur la slide**
```python
Regle(
    "DVF-01", "surface batie exploitable",
    "Une surface nulle, absente ou negative rend tout ratio au m2 indefini : "
    "la ligne ne peut ni etre comparee ni etre rapprochee.",
    lambda d: d[d["surface_reelle_bati"].notna() & (d["surface_reelle_bati"] > 0)],
),
```
> Chaque règle porte : **identifiant · libellé · justification métier · filtre**
> Le moteur compte les lignes entrantes et sortantes de chacune.
> → **le tableau avant/après est généré, il ne peut pas diverger du code.**

**Script**
> Le nettoyage. Le référentiel demande des règles écrites, la suppression des entrées corrompues,
> et un tableau avant-après.
>
> J'aurais pu enchaîner des filtres pandas. Le problème, c'est qu'au bout de dix filtres, plus
> personne ne sait lequel a supprimé quoi ni pourquoi.
>
> Chaque règle est donc un objet, qui porte un identifiant, un libellé, une justification métier
> rédigée, et le filtre lui-même. Le moteur les exécute dans l'ordre et compte, pour chacune, les
> lignes entrantes et sortantes. Conséquence : le tableau que je vais montrer est généré. Il ne
> peut pas diverger du code, puisqu'il est produit par lui.

---

## Slide 11 — C3 : le tableau avant / après · 1 min 30

**Sur la slide**

| Règle | Avant | Après | −  |
|---|---:|---:|---:|
| `DVF-01` surface bâtie exploitable | 997 | 975 | **22** |
| `DVF-02` surface plausible (≤ 2000 m²) | 975 | 967 | **8** |
| `DVF-03` valeur foncière renseignée | 967 | 947 | **20** |
| `DVF-04` type de local retenu | 947 | 922 | **25** |
| `DVF-05` déduplication des dispositions | 922 | 904 | **18** |
| `DVF-06` date de mutation valide | 904 | 900 | **4** |
| `DPE-01→04` numéro, étiquette A-G, date, doublons | 726 | 689 | **37** |

> **DVF : −9,7 % · DPE : −5,1 %** — `reports/annexes/nettoyage_avant_apres.md`

**Script**
> Voici le tableau. Chaque ligne est une règle, et chaque règle supprime des lignes réelles.
>
> J'insiste sur un point facile à rater : ce ne sont pas des règles décoratives écrites pour cocher
> une case. La règle 4 retire vingt-cinq dépendances et locaux commerciaux, parce qu'un garage n'a
> pas de diagnostic énergétique de logement comparable : le rapprocher produirait du bruit, pas de
> l'information. La règle 5 supprime dix-huit doublons — dans DVF, une mutation à plusieurs
> dispositions apparaît plusieurs fois, et sans déduplication le même bien pèserait plusieurs fois
> dans mes statistiques.
>
> Au total je retire près de dix pour cent des lignes DVF, et je peux justifier chaque suppression
> individuellement.

---

## Slide 12 — C3 : ce que le rapprochement ne sait pas · 1 min

**Sur la slide**
> Clé de rapprochement : la **parcelle cadastrale** — seul identifiant partagé.
>
> | | |
> |---|---:|
> | Rapprochements candidats | **922** |
> | Appariés à un diagnostic | **716** |
> | **Sans DPE** → conservés, **jamais scorés** | **206** |
> | Parcelles **multi-DPE** → ambiguïté comptée | **44** |
>
> **L'absence d'information est une information.**

**Script**
> Le rapprochement se fait sur la parcelle cadastrale, seul identifiant partagé entre DVF et
> l'adressage des DPE. Ce choix est discutable, et c'est précisément le sujet du projet.
>
> Il est fiable quand une parcelle porte un seul logement, et ambigu dès qu'elle en porte
> plusieurs — en copropriété. Quarante-quatre parcelles sont dans ce cas. Je ne masque pas cette
> ambiguïté : je la compte, je la stocke dans une colonne, et elle fera baisser le niveau de
> confiance en aval.
>
> Et deux cent six mutations n'ont aucun diagnostic rapprochable. Je les conserve. J'aurais pu les
> supprimer pour présenter un jeu plus propre — j'ai fait l'inverse, parce que l'absence
> d'information est une information, et qu'un système honnête doit pouvoir répondre « je ne sais
> pas ».

---

## Slide 13 — C4 : modèle de données et RGPD vérifié · 1 min 45

**Sur la slide** — MCD/MPD (`docs/data-model.md`) + :
> **PostgreSQL 17** conteneurisé, port 5433 · `reference_commune` · `exposition_alea`
> Import **idempotent** : `python scripts/import_postgres.py`
>
> Registre RGPD → **minimisation** : aucune adresse détaillée publiée par l'API.

```python
@pytest.mark.regression
def test_aucune_adresse_detaillee_n_est_publiee_par_l_api_data() -> None:
    """Verrouille l'engagement de minimisation du registre RGPD. (C4, C17)"""
    for reponse in reponses:                       # les 3 routes exposées
        assert "adresse_ban" not in reponse.text
```

**Script**
> Pour le stockage, PostgreSQL en conteneur : un SGBD relationnel complet, qui permet de vraies
> jointures, et une installation reproductible sur n'importe quelle machine. Le modèle conceptuel
> et physique sont documentés. Le script d'import est idempotent : je peux le rejouer sans créer
> de doublons.
>
> Sur le RGPD, je voudrais vous montrer une chose. J'ai un registre classique — finalité, base
> légale, minimisation, conservation, sécurité. Il engage Concorde à ne publier aucune adresse
> détaillée, parce que croiser une adresse précise, un prix de vente et une étiquette énergétique
> permet de désigner un logement, donc potentiellement son occupant.
>
> Le problème, c'est qu'un registre est un document, et que rien n'empêche le code de s'en écarter.
> C'est exactement ce qui m'est arrivé : en ajoutant des routes à l'API, j'ai exposé sans le
> vouloir le champ adresse. Le registre disait une chose, le code en faisait une autre.
>
> J'ai corrigé, et surtout j'ai écrit ce test. Il interroge les trois routes et échoue si une
> adresse réapparaît. L'engagement n'est plus une intention : c'est une contrainte vérifiée à
> chaque exécution.

---

## Slide 14 — C5 : l'API de mise à disposition · 1 min 15

**Sur la slide**
```python
@app.get("/communes", tags=["donnees"])
def communes(
    departement: Annotated[str, Query(pattern=r"^[0-9]{2}$", examples=["33"])],
    identite: Annotated[Identite, Depends(exige_role("reader"))],
) -> list[dict]:
    """Liste les communes d'un departement et leur synthese d'aleas."""
```
> `/communes` · `/rapprochements` · `/rapprochements/{id}` · `/rapprochements/demonstration` · `/sante`
> **Validation à l'entrée** (regex) · **auth par clé et par rôle** · **OpenAPI générée depuis le contrat appliqué**
> Sans clé → **401**. Entrée non conforme → **422**, avec le champ fautif nommé.

**Script**
> Dernier point : la mise à disposition, par cinq routes REST.
>
> Trois éléments sur cette signature. Le paramètre est contraint par une expression régulière —
> deux chiffres, rien d'autre : une entrée non conforme est rejetée avant d'atteindre le code
> métier, avec un message qui nomme le champ fautif. La dépendance `exige_role` impose une clé
> d'API valide et un rôle suffisant : sans clé, la route répond 401, et je peux vous le montrer en
> direct. Enfin, la documentation OpenAPI est générée à partir de ces annotations : elle décrit
> donc le contrat réellement appliqué, pas un document rédigé à côté qui pourrait dériver.

---

## Slide 15 — Récapitulatif E1 · 30 s

**Sur la slide**

| | Preuve | Commande |
|---|---|---|
| **C1** | 5/5 types, manifeste SHA-256, gestion d'erreur tracée | `python -m concorde.collect` |
| **C2** | Jointure PostgreSQL + agrégation Spark SQL, testées | `docs/queries.md` |
| **C3** | 10 règles comptées, tableau généré, 922 rapprochements | `python -m concorde.clean` |
| **C4** | MCD/MPD, PostgreSQL 17, import idempotent, **RGPD testé** | `docs/rgpd.md` |
| **C5** | 5 routes REST, auth par rôle, OpenAPI | `api/data/` |

**Script**
> Pour résumer : cinq types de sources prouvés par un manifeste, des requêtes SQL et Spark
> documentées et testées, dix règles de nettoyage dont l'effet est mesuré, une base PostgreSQL avec
> son modèle et un registre RGPD vérifié par un test, une API authentifiée et documentée.
>
> Tout est reproductible par trois commandes, et je peux exécuter n'importe laquelle devant vous.
> Je passe à la mise en service du modèle.

---

## Aide-mémoire

```bash
./scripts/soutenance.sh start     # tout, avec verification. Code 0 = pret.
```

**À montrer en direct si on te le demande**
- manifeste : `cat data/raw/_manifest.json`
- tableau avant/après : `cat reports/annexes/nettoyage_avant_apres.md`
- refus sans clé : `curl -i "http://127.0.0.1:8001/communes?departement=33"` → **401**
- documentation : `http://127.0.0.1:8001/docs`

**Si on te demande « c'est de la finance ? »**
> « Non, et c'est délibéré. Je produis la couche de fiabilité en amont d'une décision financière.
> Estimer un prix ou une solvabilité m'aurait fait entrer dans le champ haut risque du règlement
> européen sur l'IA, avec des obligations que je ne peux pas honorer sur ce périmètre. J'ai préféré
> prouver ce que je peux prouver. »
