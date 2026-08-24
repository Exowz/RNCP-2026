# Nettoyage et rapprochement — tableau avant / apres

Genere par `python -m concorde.clean`. Ne pas editer a la main.

### Jeu `dvf` — 997 lignes en entree, 900 en sortie (97 supprimees, 9.73%)

| Regle | Nature | Avant | Apres | Supprimees | Justification |
|---|---|---:|---:|---:|---|
| `DVF-01` surface batie exploitable | filtre | 997 | 975 | 22 | Une surface nulle, absente ou negative rend tout ratio au m2 indefini : la ligne ne peut ni etre comparee ni etre rapprochee. |
| `DVF-02` surface batie plausible (<= 2000 m2) | filtre | 975 | 967 | 8 | Au-dela de 2000 m2 il ne s'agit plus d'un logement mais d'un lot ou d'une saisie erronee ; le perimetre du projet est le logement. |
| `DVF-03` valeur fonciere renseignee et positive | filtre | 967 | 947 | 20 | La valeur fonciere sert de signal de coherence (pas de prediction). Absente ou nulle, elle ne porte aucune information exploitable. |
| `DVF-04` type de local retenu (Maison ou Appartement) | filtre | 947 | 922 | 25 | Les dependances et locaux industriels n'ont pas de DPE logement comparable : les rapprocher produirait du bruit, pas de l'information. |
| `DVF-05` deduplication (id_mutation, id_parcelle) | filtre | 922 | 904 | 18 | Une mutation portant plusieurs dispositions apparait plusieurs fois dans DVF+ ; sans deduplication, le meme bien pese plusieurs fois dans les scores. |
| `DVF-06` date de mutation valide | filtre | 904 | 900 | 4 | Une date non interpretable interdit de calculer l'ecart temporel avec le DPE, qui est un signal de coherence central. |

### Jeu `dpe` — 726 lignes en entree, 689 en sortie (37 supprimees, 5.10%)

| Regle | Nature | Avant | Apres | Supprimees | Justification |
|---|---|---:|---:|---:|---|
| `DPE-01` numero de DPE present | filtre | 726 | 716 | 10 | Le numero ADEME est la cle de reference du diagnostic : sans lui, l'enregistrement n'est pas verifiable a la source. |
| `DPE-02` etiquette dans l'echelle reglementaire A-G | filtre | 716 | 708 | 8 | Toute autre valeur signale un enregistrement corrompu ou hors norme. |
| `DPE-03` date d'etablissement valide | filtre | 708 | 702 | 6 | Necessaire pour situer le diagnostic par rapport a la mutation. |
| `DPE-04` deduplication par numero de DPE | filtre | 702 | 689 | 13 | Les exports ADEME successifs peuvent republier un meme diagnostic. |

### Rapprochement DVF+ x DPE

| Indicateur | Valeur |
|---|---:|
| Rapprochements candidats | 922 |
| Avec DPE apparie | 716 |
| Sans DPE (inconnue assumee) | 206 |
| Taux d'appariement | 77.66% |
| Parcelles portant plusieurs DPE (ambiguite) | 44 |