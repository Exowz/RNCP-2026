# Soutenance RNCP — Concorde

**27 août 2026, 14h00–16h30, distanciel.** Présence 30 min avant, avec pièce d'identité et convocation.

## La présentation

**→ https://gamma.app/docs/pxfmkp5lbgesf25**

**Un seul document**, 64 slides, cinq sections annoncées. Thème **Stratos** — bleu nuit,
indigo, fort contraste, typographie Geist.

En distanciel, jongler entre plusieurs onglets pendant un partage d'écran est un risque inutile :
un document unique donne au jury le même découpage, sans aucune manipulation.

## Le script

**→ `SCRIPT-COMPLET.md`** — 64 slides, numérotation **alignée 1:1 sur le deck**.

Les fichiers `E1` à `E5` restent comme sources détaillées, mais **leur numérotation ne correspond
plus** au deck consolidé. C'est `SCRIPT-COMPLET.md` qu'on lit le jour J, sur un second écran.

**~9 900 mots → ~73 minutes** à 135 mots/minute, sur 80 disponibles.

| Section | Slides | Compétences | Durée cible |
|---|---|---|---:|
| Ouverture | 1 → 6 | cadrage | — |
| **Données** | 7 → 18 | C1–C5 | 15 min |
| **Modèle et MLOps** | 19 → 31 | C9–C13 · *démo* | 20 min |
| **Application** | 32 → 44 | C14–C19 · *démo* | 20 min |
| **Service d'IA** | 45 → 54 | C6–C8 | 15 min |
| **Exploitation** | 55 → 64 | C20–C21 | 10 min |

## Les captures à insérer

Sept slides portent un marqueur `📷 INSÉRER LA CAPTURE` avec le nom du fichier.
Elles sont dans `reports/captures/`. Glisser-déposer, puis supprimer la ligne du marqueur.

| Slide | Capture |
|---|---|
| 4 — Le terrain | `12-web-accueil-atlas-schema-dvf-dpe.jpg` |
| 26 — C10 deux clients | `09-web-degradation-api-indisponible.jpg` |
| 29 — C13 chaîne de livraison | `04-ci-github-verte.png` |
| 31 — Démonstration modèle | `08-web-resultat-trois-axes-jamais-fusionnes.jpg` |
| 44 — Démonstration application | `07-web-accueil-glossaire-et-cas-reels.jpg` |
| 58 — C20 seuils et alertes | `04-surveillance-locale-seuils-alertes.jpg` |
| 60 — C21 l'incident 405 | `06-bascule-profil-corrigee.jpg` |

## Le jour J

```bash
./scripts/soutenance.sh start        # avant de te connecter — code 0 = prêt
./scripts/soutenance.sh api-model    # après la démo où tu arrêtes l'API
```

## Captures : quelles cartes, quels fichiers

Le détail complet, avec la justification de chaque placement, est dans
[`reports/captures/README.md`](../../captures/README.md).

Gamma n'a pas conservé les marqueurs d'insertion à la génération : il n'y a pas
d'emplacement préalable dans le deck. On ajoute une image en cliquant sur la carte,
puis `+` → *Image* → *Upload*. Les cartes se retrouvent par leur titre.

**Sept cartes prévues au script :** 4, 26, 29, 31, 44, 58, 60.
**Huit cartes en plus :** 6, 8, 22, 23, 24, 26 (seconde image), 41, 58 (seconde image).
**Une capture en réserve**, non placée : `19-jinja-degradation-evaluation-impossible.jpg`,
pour la question « et si le modèle tombe ? ».
