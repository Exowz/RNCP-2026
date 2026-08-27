# Captures de soutenance

Captures refaites le **26 août 2026** sur l'application locale, après la refonte
« atlas » du front Next et la passe d'accentuation des textes affichés. Elles
sont prises sur les fixtures versionnées, hors ligne, sans donnée personnelle.
Les captures antérieures sont conservées dans `perimees/` : elles montrent un
état de l'interface qui n'existe plus.

## Captures placées dans le deck

Les sept captures ci-dessous correspondent aux sept cartes repérées dans
`reports/rncp/soutenances/README.md`. Le numéro renvoie à la carte du Gamma.

| Carte | Fichier | Ce que la capture prouve | Compétences |
|---|---|---|---|
| 4 | `12-web-accueil-atlas-schema-dvf-dpe.jpg` | Deux bases décrivent le même logement sans clé commune | C10, C14 |
| 26 | `09-web-degradation-api-indisponible.jpg` | Le client refuse d'afficher un résultat partiel quand l'amont tombe | C10, C17 |
| 29 | `04-ci-github-verte.png` | Le workflow `Verification Concorde` a réellement été exécuté | C13, C18, C19 |
| 31 | `08-web-resultat-trois-axes-jamais-fusionnes.jpg` | Cohérence, atypicité et confiance restituées séparément, avec leurs échelles | C9, C12 |
| 44 | `07-web-accueil-glossaire-et-cas-reels.jpg` | Le vocabulaire métier est posé avant le résultat ; cinq cas réels | C10, C14, C17 |
| 58 | `04-surveillance-locale-seuils-alertes.jpg` | Seuils d'alerte explicites et surveillance strictement locale | C20 |
| 60 | `06-bascule-profil-corrigee.jpg` | La bascule de profil répond 200 : l'incident C21 est corrigé | C21 |

## Captures additionnelles, et leur carte

Placées en plus des sept ci-dessus. Le numéro renvoie à la carte du Gamma ; le titre
permet de retrouver la carte dans l'éditeur, où l'on ajoute l'image par `+` puis *Image*.

| Carte | Titre de la carte | Fichier | Pourquoi là |
|---|---|---|---|
| 6 | Ce que Concorde fait, et ne fait pas | `15-web-comment-ca-marche-ce-qui-est-compare.jpg` | L'interface écrit « le prix est un signal de cohérence, jamais une prédiction » |
| 8 | La chaîne, avec ses volumes réels | `10-web-comment-ca-marche-chaine-et-volumes.jpg` | Affiche 1 743 → 922 → 716 → 206 |
| 22 | La métrique honnête | `16-web-transparence-fiche-modele-et-limites.jpg` | La fiche assume la circularité du rappel des règles |
| 23 | Les cinq règles, et d'où viennent leurs seuils | `11-web-transparence-regles-seuils-gravite.jpg` | COH-01 à COH-05 avec seuil et gravité, servis par l'API |
| 24 | L'artefact gelé : tout ce qu'il faut pour rejouer | `14-web-resultat-decomposition-ecart-version-modele.jpg` | La version du modèle est servie avec le résultat |
| 26 | C10 — Deux clients indépendants de la même API | `18-resultat-jinja-profil-analyste.jpg` (avec `09`) | Les deux clients, côte à côte |
| 41 | C17 — Intégrer un service d'IA sans lui donner autorité | `13-web-resultat-elements-qui-fondent-la-conclusion.jpg` | L'explication déjà calculée que le LLM reformule |
| 58 | C20 — Seuils, alertes, tableau de bord | `17-surveillance-metriques-par-route.jpg` (avec `04`) | Même page : les seuils en haut, les métriques en bas |

## Capture gardée en réserve

`19-jinja-degradation-evaluation-impossible.jpg` — **volontairement non placée.**
À ouvrir si le jury demande « et si le modèle tombe ? » : elle montre que l'application
de repli refuse de conclure exactement comme le front Next.

## Détail des captures additionnelles


| Fichier | Ce qu'elle apporte | Compétences |
|---|---|---|
| `10-web-comment-ca-marche-chaine-et-volumes.jpg` | La chaîne et ses volumes réels : 1 743 → 922 → 716 → 206 | C1, C3 |
| `11-web-transparence-regles-seuils-gravite.jpg` | Les règles de cohérence servies par l'API, avec seuil et gravité | C11, C17 |
| `13-web-resultat-elements-qui-fondent-la-conclusion.jpg` | La justification nommée derrière un verdict | C9, C12 |
| `14-web-resultat-decomposition-ecart-version-modele.jpg` | Version du modèle servie et part de chaque variable dans l'écart | C12, C19 |
| `15-web-comment-ca-marche-ce-qui-est-compare.jpg` | Ce qui est comparé, ce qui est rendu visible | C14, C17 |
| `16-web-transparence-fiche-modele-et-limites.jpg` | Fiche du modèle et **limites assumées** | C11, C17 |
| `17-surveillance-metriques-par-route.jpg` | Métriques par route mesurées sur le trafic réel de la session | C20 |
| `18-resultat-jinja-profil-analyste.jpg` | Vue analyste de l'application de repli | C10 |
| `19-jinja-degradation-evaluation-impossible.jpg` | Même refus de conclure côté application de repli | C10, C17 |

## Reproduire ces captures

```bash
./scripts/soutenance.sh start          # les quatre services
# la dégradation (cartes 26 et 19) se reproduit en arrêtant l'API modèle :
kill $(lsof -ti tcp:8002)
./scripts/soutenance.sh api-model      # puis en la relançant
```
