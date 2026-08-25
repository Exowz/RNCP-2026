# Veille technique et réglementaire — C6

Dernière revue : 25 août 2026. Responsable : candidat seul. La veille est
partagée dans ce dépôt par commits et décisions tracées ; aucun collectif fictif
n’est simulé.

## Agrégation réellement configurée

[`veille.opml`](veille.opml) est un fichier OPML importable dans un lecteur RSS
local (par exemple Thunderbird ou un lecteur installé sur le poste). Il contient
les flux officiels disponibles d’ADEME, CNIL, PyPI et des dépendances critiques
sur GitHub. L’import se fait une fois avant la démonstration ; la lecture des
éléments déjà synchronisés reste possible hors ligne.

data.gouv.fr et Géorisques ne publient pas de flux RSS stable pour les jeux de
données suivis : les URL RSS candidates ont répondu 404 lors de cette revue. Le
fichier OPML conserve donc leurs pages officielles comme repères de consultation
manuelle, sans les présenter comme des flux. Cette limite est volontairement
visible plutôt que masquée par un service d’agrégation en ligne non configuré.

Rythme : chaque matin jusqu’à la soutenance, puis hebdomadaire. Une alerte qui
modifie le contrat, la sécurité, une source ou une dépendance déclenche une
entrée dans `docs/journal-decisions.md`, une preuve adaptée et, si nécessaire,
un incident. Une source ne devient jamais une exigence automatique : elle est
interprétée dans le périmètre de Concorde.

## Grille de fiabilité des sources

| Source | Usage | Fiabilité | Pourquoi on la garde |
|---|---|---|---|
| [ADEME — publications Bâtiment](https://librairie.ademe.fr/rss/3153-thematique-batiment.xml) | Contexte DPE et limites d’interprétation énergétique. | **Auteur** : ADEME ; **date** : datée par publication ; **primaire** : oui, producteur institutionnel ; **convergence** : rapprochée de data.gouv.fr et du contrat DPE ; **accessibilité** : flux RSS public ; **biais** : vue institutionnelle, pas une mesure exhaustive du parc. | Source métier primaire, accessible sans compte et adaptée aux réserves affichées. |
| [data.gouv.fr — DVF](https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres/) | Disponibilité, licence et évolution de la donnée DVF. | **Auteur** : administration productrice publiée par data.gouv.fr ; **date** : métadonnées datées, consultées le 25 août ; **primaire** : oui pour la diffusion officielle ; **convergence** : comparée au schéma collecté et aux notices DVF ; **accessibilité** : page publique, sans flux stable ; **biais** : ne décrit pas seule la qualité du rapprochement. | Référence de provenance de la première source, malgré l’absence déclarée de RSS. |
| [Géorisques — bases de données](https://www.georisques.gouv.fr/donnees/bases-de-donnees) | Périmètre et limites de l’exposition aux aléas. | **Auteur** : ministère / Géorisques ; **date** : métadonnées du jeu, consultées le 25 août ; **primaire** : oui pour la diffusion réglementaire ; **convergence** : comparée au champ `exposition_aleas` et à la documentation de limite communale ; **accessibilité** : page publique, sans flux stable ; **biais** : granularité qui ne remplace pas une expertise parcellaire. | Empêche de présenter l’aléa communal comme une information de parcelle. |
| [CNIL — recommandations IA et RGPD](https://www.cnil.fr/fr/developpement-des-systemes-dia-les-recommandations-de-la-cnil-pour-respecter-le-rgpd) | Finalité, minimisation, information et arrêt d’un service IA. | **Auteur** : CNIL ; **date** : publiée et mise à jour par la CNIL ; **primaire** : oui, autorité compétente ; **convergence** : comparée aux contrôles d’accès, au registre RGPD et au contrat `/expliquer` ; **accessibilité** : flux CNIL public dans l’OPML ; **biais** : cadre de conformité, pas prescription d’architecture détaillée. | Justifie l’usage local et borné du LLM, sans lui attribuer de décision. |
| [PyPI — mises à jour](https://pypi.org/rss/updates.xml) | Publication de versions Python et signal faible de maintenance. | **Auteur** : Python Package Index ; **date** : horodatage de chaque publication ; **primaire** : oui pour la diffusion de paquet ; **convergence** : confrontée à `uv.lock`, `pip-audit` et notes de version ; **accessibilité** : flux public ; **biais** : publication n’équivaut pas à correctif de sécurité. | Complète l’audit, sans le remplacer. |
| [GitHub — releases DVC](https://github.com/iterative/dvc/releases.atom) et [MLflow](https://github.com/mlflow/mlflow/releases.atom) | Changements des dépendances critiques de la chaîne MLOps. | **Auteur** : organisations mainteneuses ; **date** : datée par release ; **primaire** : oui pour leur code ; **convergence** : comparée à PyPI, `pip-audit` et tests locaux ; **accessibilité** : flux Atom public ; **biais** : annonce éditeur à vérifier avant montée de version. | Cible les paquets qui ont déjà affecté l’audit ou la reproductibilité. |

La limite assumée reste l’absence d’animation d’équipe : la compétence est
prouvée par la qualification, le rythme et les décisions reproductibles, pas par
une réunion inventée.
