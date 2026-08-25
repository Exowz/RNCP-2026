# Remédiation de soutenance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rendre la démo locale redémarrable et fermer les écarts objectifs de preuve, tests et sécurité.

**Architecture:** Un lanceur Python orchestre les prérequis locaux dans un environnement Java 17 déterministe. Les tests d'intégration couvrent les frontières C1/C3/C21 ; les documents et captures rendent ces preuves navigables pendant la soutenance.

**Tech Stack:** Python 3.12, pytest, Docker Compose, PostgreSQL 17, Spark 3.5, PyTorch.

**Spec:** `docs/superpowers/specs/2026-08-25-remediation-soutenance-design.md`

## Global Constraints

- Ne jamais télécharger de dépendance ni de données pendant la démonstration.
- Le lanceur ne masque pas un LM Studio absent : il donne une erreur actionnable.
- Toute évolution de code est protégée par un test de comportement.
- Les captures montrent des résultats réels, sans données personnelles.

---

### Task 1: Prévol reproductible

**Files:**
- Create: `src/concorde/demo.py`, `scripts/demarrer_demo.py`, `tests/test_demo.py`
- Modify: `README.md`, `scripts/spark-env.sh`

- [x] Écrire les tests rouges de sélection Java 17 et de refus explicite d'un service LM indisponible.
- [x] Implémenter le lanceur : résolution Java, PostgreSQL, import, prévol LM Studio et pytest.
- [x] Exécuter les tests unitaires puis la commande complète avec le service local disponible.

### Task 2: Tests C1, C3 et C21

**Files:**
- Create: `tests/data/test_collecte_fichier.py`, `tests/data/test_rapprochement.py`, `tests/data/test_regression_initialisation.py`

- [x] Vérifier le collecteur DVF réel et son refus de schéma incomplet.
- [x] Vérifier le rapprochement réel, y compris une mutation conservée sans DPE.
- [x] Rejouer l'import PostgreSQL avant la collecte avec `@pytest.mark.regression`.

### Task 3: Chargement sûr et documentation

**Files:**
- Modify: `src/concorde/model/moteur.py`, `tests/model/test_entrainement.py`, `BRIEF.md`, `docs/journal-decisions.md`, `reports/rncp/E3.md`, `README.md`
- Create: `reports/captures/README.md`

- [x] Écrire le test rouge qui refuse un artefact PyTorch exécutable.
- [x] Passer au chargement strict `weights_only=True` et vérifier Bandit.
- [x] Mettre à jour les renvois et l'état de la matrice ; indexer les captures réelles.
