# Les cinq soutenances

**27 août 2026, 14h00–16h30, distanciel.** Présence 30 min avant, avec pièce d'identité et convocation.

## Ordre de passage et liens Gamma

| Ordre | Épreuve | Durée | Script mesuré | Slides Gamma |
|---|---|---:|---:|---|
| 1 | **E1** — Données (C1–C5) | 15 min | 13,7 | https://gamma.app/docs/rzi5n6cuczl0hbl |
| 2 | **E3** — Modèle et MLOps (C9–C13) · *démo* | 20 min | 17,9 | https://gamma.app/generations/SvS7eOLCN6cD68t2iy2V4 |
| 3 | **E4** — Application (C14–C19) · *démo* | 20 min | 16,8 | https://gamma.app/docs/48qtur4yuu5oqfg |
| 4 | **E2** — Service IA (C6–C8) | 15 min | 12,8 | https://gamma.app/docs/fwho0dhqwubdksc |
| 5 | **E5** — Monitorage et incident (C20–C21) | 10 min | 9,6 | https://gamma.app/docs/x66pe71fi2w0apu |

**Total parole : 70,8 min sur 80.** La marge réelle est plus faible sur E3 et E4, dont les
démonstrations consomment du temps d'interaction non compté ici.

## Comment utiliser ces fichiers

Les fichiers `E*.md` contiennent **le script à lire**, slide par slide. Les Gammas ne contiennent
que **le contenu des slides** : garde le markdown sur un second écran ou imprimé.

## Avant de te connecter

```bash
./scripts/soutenance.sh start      # code de sortie 0 = tout est prêt
```

Et pendant E4, après la démonstration où tu arrêtes volontairement l'API :

```bash
./scripts/soutenance.sh api-model
```

## Captures à insérer dans Gamma

Elles sont dans `reports/captures/`. Les principales :

| Capture | Où l'insérer |
|---|---|
| `12-web-accueil-atlas-schema-dvf-dpe.jpg` | E1 slide « Le terrain » |
| `04-ci-github-verte.png` | E3 « chaîne de livraison », E4 « C18 » |
| `08-web-resultat-echelles-expliquees.jpg` | E3 démonstration |
| `09-web-degradation-api-indisponible.jpg` | E3 « C10 », E4 démonstration |
| `04-surveillance-locale-seuils-alertes.jpg` | E5 « seuils et alertes » |
| `03-resultat-analyste-decomposition-ecart.jpg` | E3 « vue analyste » |
