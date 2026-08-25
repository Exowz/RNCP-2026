# Passation — état du projet et reste à faire

**Document de reprise.** À lire en premier par toute session (Claude Code, Codex) qui reprend
le projet. Dernière mise à jour : 25 août 2026.

> ⚠️ **Le dépôt est public.** Ne jamais y committer la convocation du candidat (données
> personnelles) ni les PDF de coaching (supports de K. Kadri / Simplon / ECE, droit d'auteur).
> Ils vivent dans `docs/coaching-source/`, qui est **gitignoré**. Textes déjà extraits en `.txt`
> dans ce même dossier — les lire plutôt que les PDF, c'est plus économe.

---

## 1. Le format réel de l'épreuve — information critique

Découvert le 25 août dans la convocation officielle. **Ce n'est pas une présentation continue
de 80 minutes**, contrairement à ce que supposait le brief initial.

**27 août 2026, 14h00 – 16h30, en distanciel.** Présence 30 minutes avant, avec pièce d'identité
et convocation.

| Ordre | Épreuve | Durée | Contenu |
|---|---|---:|---|
| — | Installation | 5 min | matériel et supports |
| 1 | **E1** — C1–C5 | **15 min** | collecte, stockage, mise à disposition des données |
| 2 | **E3** — C9–C13 | **20 min** | intégration modèles et services IA · **avec démonstration** |
| 3 | **E4** — C14–C19 | **20 min** | application intégrant un service IA · **avec démonstration** |
| 4 | **E2** — C6–C8 | **15 min** | installation et configuration du service IA préconisé |
| 5 | **E5** — C20–C21 | **10 min** | monitorage applicatif et résolution d'incident |
| — | Échanges avec le jury | 10 min | questions sur les compétences insuffisamment détaillées |
| — | Délibération | 10 min | en l'absence du candidat |

Total : **80 min de présentation + 10 min de questions**.

### Trois conséquences

1. **Cinq supports distincts**, pas un seul. Chacun doit tenir seul, avec son propre fil.
2. **E2 passe en quatrième position**, après les deux démos. Il faut l'assumer comme un retour en
   arrière : « voici pourquoi ce service, que vous venez de voir tourner ».
3. **Distanciel** : la démonstration passe par partage d'écran. Les quatre services et le build
   Next.js doivent tourner **avant** la connexion. À répéter au moins une fois en conditions réelles.

### Ce que les camarades rapportent

Aucun rapport écrit n'a jamais été réclamé. Les rapports ont servi à structurer la présentation, rien
de plus. Les supports contenaient **des captures d'écran et des extraits de code**. Le coaching le
confirme à chaque séance : *« capture GitHub Actions verte + fichier workflow versionné +
interprétation des étapes »* — le code est attendu **commenté**, pas décoratif.

---

## 2. État technique : terminé des deux côtés

| Indicateur | Valeur |
|---|---|
| Tests | **49** (48 hors marqueur `local_service`), couverture **86 %** |
| Porte de conformité | **12 critères** sur 3 axes, exécutable et bloquante |
| Incidents documentés | **5**, chacun vérifié dans les deux sens |
| Sources collectées | **5 types** exigés, 6 collecteurs |
| Rapprochements | **922** — 716 appariés, **206 non évaluables assumés** |
| Modèle | AUC **0,9095** (auto-encodeur seul, métrique informative) |
| Captures | 16 |
| CI | verte, chaîne complète |
| Compétences | **19 prouvées · 2 partielles assumées (C6, C16) · 0 non traitée** |

Matrice détaillée : `reports/rncp/matrice-preuves.md`. Mémo : la matrice de `BRIEF.md`.

### Commandes de vérification

```bash
source scripts/spark-env.sh          # JDK 17 + SPARK_LOCAL_IP — indispensable, sinon Spark casse
docker compose up -d                 # PostgreSQL 17 sur 5433
export PATH="$HOME/.lmstudio/bin:$PATH" && lms server start   # service IA local (C8)

python -m concorde.collect && python -m concorde.clean
python -m concorde.model.entrainement
pytest -m "not local_service"        # 48 verts
python scripts/conformite.py         # CONFORME (12 critères), code de sortie 0
```

### Lancer la pile de démonstration

```bash
.venv/bin/uvicorn api.data.main:app  --host 127.0.0.1 --port 8001 &
.venv/bin/uvicorn api.model.main:app --host 127.0.0.1 --port 8002 &
.venv/bin/uvicorn app.main:app       --host 127.0.0.1 --port 8000 &
cd app/web && bun run build && bun run start          # :3000
```

Ports : `3000` front Next.js · `8000` app Jinja · `8001` API data · `8002` API modèle ·
`5433` PostgreSQL · `1234` LM Studio.

---

## 3. Reste à faire

### 3.1 Quatre manques techniques, tous sur le Bloc 2 (E2)

Identifiés en confrontant nos documents aux exigences de la **séance 5** du coaching. E2 est la
soutenance la plus fragile.

| # | Manque | Exigence exacte | Fichier à modifier |
|---|---|---|---|
| 1 | **Grille de fiabilité des sources** | Séance 5 : *« Accumuler des liens sans expliquer leur fiabilité ne prouve pas la compétence. »* Table `source / usage / fiabilité / pourquoi on la garde`, six critères : auteur, date, source primaire, convergence, accessibilité, biais. | `docs/veille.md` |
| 2 | **Outil d'agrégation de flux** | Référentiel : *« Choix d'un outil d'agrégation des flux d'informations »* + sa configuration. Rien aujourd'hui. Faisable seul (RSS). | `docs/veille.md` |
| 3 | **Besoin IA reformulé** | Séance 5 : slide dédiée — contexte métier, entrées, sorties, contraintes, **critères de réussite**. Passer de « nous avons choisi X » à « voici pourquoi X répond au besoin mieux que les alternatives ». | `docs/benchmark.md` |
| 4 | **Colonnes de la matrice de benchmark** | Séance 5 attend `Fonctionnel / Technique / Risque / Décision`. Nous avons `Accès local / Modèle / Coût / Décision` : le **risque** et l'adéquation **fonctionnelle** manquent. | `docs/benchmark.md` |

**Mineur** : le Kanban de `docs/pilotage.md` est périmé — il annonce « En cours » pour C12–C13 et
le bloc 3, qui sont terminés.

### 3.2 Réécrire le conducteur en cinq supports

`reports/rncp/conducteur-soutenance.md` **est à refaire** : il vise une narration continue de
80 minutes, ce qui ne correspond pas au format réel. Il faut cinq conducteurs minutés (15/20/20/15/10),
chacun avec :

- le fil de la soutenance et le minutage,
- les captures à montrer (nommées, elles sont dans `reports/captures/`),
- les **extraits de code** à afficher et ce qu'on en dit,
- pour E3 et E4 : le **script de démonstration** pas à pas.

Les questions du jury et leurs réponses en deux phrases sont déjà rédigées dans l'actuel
`conducteur-soutenance.md`, section finale — **à conserver telle quelle**.

### 3.3 Puis les supports eux-mêmes

Présentation RNCP (5 decks) et rapport du projet de substitution n°21.

---

## 4. Ce qu'il ne faut pas casser

Six compétences sont vertes et prouvées. Ne pas toucher sans raison :

| Chemin | Ce qu'il porte |
|---|---|
| `app/main.py`, `app/templates/`, `app/static/` | C10, C14, C17, C20 — app Jinja, **livrable évalué** |
| `app/web/` | second client Next.js — clé d'API **côté serveur uniquement** (`server-only`) |
| `api/model/`, `api/data/` | C5, C9 |
| `src/concorde/**` | C1–C3, C11–C13 |
| `.github/workflows/verify.yml` | C18 — CI verte |
| `scripts/conformite.py` | livrable central du n°21 |
| `tests/**` | C12 — 49 tests |

### Règles apprises à la dure

1. **Les valeurs de contrat restent en ASCII.** `eleve`, `a_verifier`, `majeur`, `penalite`,
   `reserves` sont des identifiants d'API, pas du texte. Les accentuer casse les schémas Pydantic
   et tous les clients. Elles sont traduites à l'affichage : `app/main.py` côté Jinja,
   `app/web/lib/libelles.ts` côté Next.
2. **Hors ligne, sans exception.** Aucun CDN, aucune police distante (pas de `next/font/google`,
   qui télécharge au *build*), aucun remote DVC distant. Le garde-fou socket
   (`src/concorde/common/offline.py`) transforme toute sortie non locale en erreur.
3. **`source scripts/spark-env.sh` est obligatoire.** Il fixe `JAVA_HOME` sur le JDK 17 (le JDK 26
   du système fait échouer Spark) et `SPARK_LOCAL_IP=127.0.0.1` (sinon Spark cherche l'adresse
   mDNS du poste, indisponible hors ligne).
4. **Vérifier, pas déclarer.** Exécuter la commande et lire la sortie. Un test de non-régression
   doit être vérifié **dans les deux sens** : on retire le correctif et l'on confirme que le test
   échoue. Un test rendu hermétique peut avoir perdu son pouvoir de détection.
5. **La documentation qui ment est le défaut récurrent du projet** — quatre incidents sur cinq.
   Registre RGPD annonçant une minimisation non appliquée, `.gitignore` affirmant un versionnement
   DVC inexistant, `docs/securite.md` affirmant que `mlflow-skinny` couvrait le tracking SQLite.
   Chaque correction a rendu l'affirmation vraie **et** l'a fait vérifier par un test ou un critère.

---

## 5. Le projet en trois phrases

Concorde évalue si le rapprochement entre une **vente immobilière** (DVF+) et un **diagnostic
énergétique** (DPE ADEME) est fiable, en le croisant avec l'exposition aux aléas (Géorisques).
Il répond à trois questions **jamais fusionnées** : les deux enregistrements se contredisent-ils
(cohérence, règles explicites), ce rapprochement ressemble-t-il aux autres (anomalie, auto-encodeur
PyTorch), peut-on se fier à cette réponse (confiance, complétude et précision).

**Il n'estime aucun prix et ne produit aucune tarification.** Ce n'est pas une lacune, c'est un
choix de périmètre : estimer une valeur ou une solvabilité ferait entrer le projet dans le champ
haut risque du règlement européen sur l'IA.

Ligne de défense : *« je ne remplace pas la décision ; je réduis l'écart entre des données
complexes et une décision informée, en rendant visibles les sources, les hypothèses et les
inconnues. »*
