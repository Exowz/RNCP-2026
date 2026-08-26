# Les cinq soutenances

**27 août 2026, 14h00–16h30, distanciel.** Présence 30 min avant, avec pièce d'identité et convocation.

## La présentation

**Un seul document Gamma**, cinq sections annoncées — pas cinq documents.
En distanciel, jongler entre plusieurs onglets pendant un partage d'écran est un risque inutile :
un document unique donne au jury le même découpage, et ne te demande aucune manipulation.

Thème **Petrol** — bleu de Prusse et écru, géométrique. La palette des plans cadastraux,
et un fond clair sur lequel tes captures d'application sombre ressortent nettement.

## Ordre de passage et minutage

| Ordre | Épreuve | Compétences | Durée | Script mesuré |
|---|---|---|---:|---:|
| 1 | **E1** — Données | C1–C5 | 15 min | 13,7 |
| 2 | **E3** — Modèle et MLOps · *démo* | C9–C13 | 20 min | 17,9 |
| 3 | **E4** — Application · *démo* | C14–C19 | 20 min | 16,8 |
| 4 | **E2** — Service IA | C6–C8 | 15 min | 12,8 |
| 5 | **E5** — Monitorage et incident | C20–C21 | 10 min | 9,6 |

**Total parole : 70,8 min sur 80.** La marge réelle est plus faible sur E3 et E4, dont les
démonstrations consomment du temps d'interaction non compté ici.

## Comment utiliser ces fichiers

Les fichiers `E*.md` contiennent **le script à lire**, slide par slide. La présentation Gamma ne
porte que **le contenu à projeter** : garde le markdown sur un second écran ou imprimé.

La slide doit se suffire à elle-même ; le script ajoute le détail et confirme la compréhension.

## Avant de te connecter

```bash
./scripts/soutenance.sh start      # code de sortie 0 = tout est prêt
```

Pendant E4, après la démonstration où tu arrêtes volontairement l'API :

```bash
./scripts/soutenance.sh api-model
```

## Captures à insérer dans Gamma

Elles sont dans `reports/captures/`.

| Capture | Section |
|---|---|
| `12-web-accueil-atlas-schema-dvf-dpe.jpg` | E1 — « Le terrain » |
| `04-ci-github-verte.png` | E3 — « chaîne de livraison » · E4 — « C18 » |
| `08-web-resultat-echelles-expliquees.jpg` | E3 — démonstration |
| `09-web-degradation-api-indisponible.jpg` | E3 — « C10 » · E4 — démonstration |
| `03-resultat-analyste-decomposition-ecart.jpg` | E3 — « vue analyste » |
| `04-surveillance-locale-seuils-alertes.jpg` | E5 — « seuils et alertes » |
