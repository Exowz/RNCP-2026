# Explication locale du verdict E2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ajouter une reformulation locale, non décisionnelle et dégradable, puis compléter les preuves documentaires E2.

**Architecture:** `/expliquer` accepte une projection Pydantic réduite du verdict déjà calculé. L’API tente LM Studio puis retourne le texte assemblé; le Server Component Next.js l’appelle sans exposer la clé.

**Tech Stack:** Python 3.12, FastAPI, Pydantic v2, httpx, pytest, Next.js 16/React 19, TypeScript, OPML.

**Spec:** `docs/superpowers/specs/2026-08-25-explication-locale-e2-design.md`

## Global Constraints

- Ne pas modifier `src/concorde/model/**`, `app/main.py`, les gabarits Jinja, `api/data/`, `scripts/conformite.py` ni `.github/workflows/verify.yml`.
- `/predict` demeure inchangé; `/expliquer` exige `reader` et exclut toute donnée brute, adresse et identifiant de parcelle.
- LM Studio est optionnel; la CI vérifie le repli et les tests réels restent `local_service`. L’appel a un délai de 3 secondes et un budget de 90 tokens.
- La sortie LLM est limitée à 1 000 caractères et rendue comme texte React, sans HTML ni Markdown.
- La clé reste `CONCORDE_API_KEY` côté serveur; aucun appel externe n’est ajouté.

### Task 1: Contrat et repli API

**Files:** `api/model/schemas.py`, `api/model/main.py`, `tests/api/test_api_modele.py`.

**Interfaces:** `ExplicationEntree` contient uniquement `statut`, `niveau_anomalie`, `score_coherence`, `motifs`, `confiance`, `explication`; `ExplicationSortie` contient `texte` et `source` (`modele_local` ou `texte_assemble`).

- [x] Écrire `test_expliquer_replie_sur_texte_assemble_si_lm_studio_est_absent` qui remplace `ClientLMStudio.reformuler_verdict` par une levée `ServiceIADisponible`, POSTe une projection réduite avec la clé reader et attend HTTP 200, le texte original et `source=texte_assemble`.
- [x] Ajouter les deux schémas stricts et la route `POST /expliquer` qui appelle le client, puis replie sur `verdict.explication` seulement en cas de `ServiceIADisponible`.
- [x] Exécuter `source scripts/spark-env.sh && .venv/bin/python -m pytest tests/api/test_api_modele.py -v`; le test de repli est vert.

### Task 2: Appel LM Studio borné et observé

**Files:** `src/concorde/service/lm_studio.py`, `tests/model/test_lm_studio_service.py`, `docs/service-ia.md`.

**Interfaces:** `ClientLMStudio.reformuler_verdict(verdict: dict[str, object]) -> str` retourne un texte borné ou lève `ServiceIADisponible`; chaque tentative enregistre `/v1/chat/completions`, statut, latence et compteurs dans `monitoring/model/metriques_lm_studio.json`.

- [x] Écrire le test `local_service` qui appelle `reformuler_verdict` avec la projection stricte et vérifie un texte non vide de 1 000 caractères au plus.
- [x] Implémenter un POST local à `/v1/chat/completions` avec `temperature=0`, `max_tokens=90`, `timeout=3.0`; le code choisit une instruction déterministe, sans envoyer le verdict au modèle. Il valide JSON, fin normale et zéro token de raisonnement, borne à 1 000 caractères et transforme tout incident en `ServiceIADisponible` après métriques.
- [x] Documenter au présent les paramètres, données exclues, repli, provenance, métriques et test dans `docs/service-ia.md`.
- [x] Exécuter `source scripts/spark-env.sh && .venv/bin/python -m pytest -m "not local_service" -q`; les tests non locaux sont verts sans dépendre de LM Studio.

### Task 3: Affichage particulier non autoritaire et sûr

**Files:** `app/web/lib/concorde.ts`, `app/web/app/resultat/[id]/page.tsx`, `app/web/components/resultat.tsx`.

**Interfaces:** le module `server-only` produit `expliquer(verdict: Verdict): Promise<Explication>`; `Resultat` reçoit une explication additionnelle seulement pour `profil === "particulier"`.

- [x] Ajouter le type, le helper qui n’envoie que la projection contractuelle, et le repli Next sur `verdict.explication` si la route optionnelle échoue.
- [x] Afficher un `aside` textuel avec provenance discrète et explicite; conserver scores, motifs et réserves calculés en place. Ne jamais utiliser `dangerouslySetInnerHTML`, Markdown ou appel navigateur.
- [x] Exécuter `cd app/web && bun run build`, `grep -rn "NEXT_PUBLIC.*KEY" .` et `grep -rn "dangerouslySetInnerHTML" app components lib`; build vert et aucun match applicatif.

### Task 4: Preuves C6, C7 et C8

**Files:** `docs/veille.opml`, `docs/veille.md`, `docs/benchmark.md`, `docs/pilotage.md`, `docs/journal-decisions.md`.

- [x] Créer un OPML importable pour les sources qualifiées ADEME, CNIL, data.gouv.fr, Géorisques et les flux GitHub/PyPI des dépendances critiques; documenter un agrégateur local et la fréquence de revue sans prétendre utiliser un compte en ligne.
- [x] Ajouter pour chaque source la grille `auteur, date, primaire, convergence, accessibilité, biais` dans les colonnes `source | usage | fiabilité | pourquoi on la garde`.
- [x] Ajouter à `benchmark.md` : contexte métier, entrées, sorties, contraintes coût/latence/sécurité/RGPD/local-cloud/accessibilité, critères de réussite; employer la matrice `Service | Fonctionnel | Technique | Risque | Décision` sans perdre les choix écartés.
- [x] Dater le Kanban de `pilotage.md`, marquer C12–C13 et Bloc 3 terminés, puis tracer la borne LLM et le choix OPML dans le journal.
- [x] Exécuter `grep -rn "utiliseront\\|permettra\\|sera " docs/service-ia.md` et `git diff --check`; aucune annonce de capacité inexistante ni erreur d’espacement.

### Task 5: Vérification intégrée

**Files:** aucune modification sauf correction prouvée nécessaire.

- [x] Exécuter `source scripts/spark-env.sh && .venv/bin/python -m pytest -m "not local_service" -q`; les tests non locaux sont verts.
- [x] Exécuter `source scripts/spark-env.sh && .venv/bin/python scripts/conformite.py` et `curl -i http://127.0.0.1:8000/sante`; la porte retourne 0 et Jinja répond HTTP 200.
- [x] Avec LM Studio démarré, tester l’appel borné; avec le service simulé absent, exécuter le test de repli. Les deux chemins ont été observés.

## Self-review

- Spec coverage: les tâches 1–3 couvrent route, non-autorité, contenu borné, métriques, repli et affichage serveur; la tâche 4 couvre C6/C7/C8; la tâche 5 couvre les preuves exécutables.
- Placeholder scan: aucun `TBD`, `TODO` ou interface implicite.
- Type consistency: `ExplicationEntree` est l’unique entrée API; `ExplicationSortie` devient `Explication` côté Next et les deux sources possibles sont identiques.
