# Remédiation de soutenance — conception

## Objectif

Rendre la démonstration locale reproductible après redémarrage, compléter les preuves demandées et fermer les écarts de sécurité et de non-régression identifiés lors de l'audit.

## Décisions

- Un lanceur Python local prépare Java 17, démarre PostgreSQL, attend son état sain, importe les références, vérifie LM Studio et lance les tests dans le même environnement. LM Studio est lancé en option sur macOS ; le script échoue avec une consigne explicite si le serveur ou le modèle ne sont pas prêts.
- Le choix de Java ne dépend pas de Homebrew ni du réseau : `JAVA_HOME` est conservé s'il pointe vers Java 17, sinon macOS résout le JDK avec `/usr/libexec/java_home -v 17`.
- Les tests couvrent les collecteurs fichier et le rapprochement avec les fixtures livrées. Un test marqué `regression` reproduit l'ordre déterminant : importer PostgreSQL avant la collecte.
- Le chargement PyTorch refuse les objets arbitraires avec `weights_only=True` ; les artefacts Concorde ne contiennent que tenseurs et types primitifs.
- Les captures sont obtenues depuis l'application et la preuve de test, puis indexées dans un guide de soutenance. La matrice du brief devient un tableau de renvoi vers les preuves réelles.

## Critères d'acceptation

1. `uv run python scripts/demarrer_demo.py` prépare les dépendances, vérifie LM Studio et produit une suite verte quand le modèle local est chargé.
2. La suite n'utilise jamais le JDK 26 pour Spark.
3. `pytest -m regression` exécute une preuve automatisée de l'incident C21.
4. Bandit ne relève plus B614 dans `moteur.py`.
5. Les modules C1/C3 précédemment non testés possèdent des tests de comportement et les artefacts de soutenance sont indexés.
