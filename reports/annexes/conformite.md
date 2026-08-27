# Tableau de conformité Secure MLOps

Généré le 2026-08-27T09:40:27.342238+00:00. Ce fichier est produit par `python scripts/conformite.py`; ne pas l'éditer à la main.

**Verdict global : CONFORME**

| ID | Axe | Critère | Seuil | Valeur mesurée | Verdict | Justification du seuil |
| --- | --- | --- | --- | --- | --- | --- |
| qualite.couverture_tests | qualité | Tests automatisés et couverture | suite verte et couverture >= 75 % | 85% | conforme | 75 % est le plancher annoncé pour le projet de substitution; la suite doit aussi rester verte. |
| qualite.auc_autoencodeur | qualité | Pouvoir discriminant de l'autoencodeur | AUC >= 0,80 | AUC 0.9095 | conforme | 0,80 constitue le minimum documenté pour distinguer utilement les cas atypiques des cas ordinaires. |
| qualite.artefact_et_contrat | qualité | Artefact PyTorch et contrat des variables | artefact présent, chargeable et variables attendues à l'identique | présent (concorde_moteur.pt), chargeable, contrat conforme | conforme | Un modèle non chargeable ou dont les variables diffèrent ne peut pas produire une prédiction reproductible. |
| qualite.chaine_entrainement | qualite | Chaine d'entrainement rejouable | `entrainer_et_geler` s'execute sans erreur, journalisation MLflow comprise | chaine rejouee sans erreur | conforme | Un artefact valide sur le disque ne prouve pas que la chaine qui l'a produit fonctionne encore. Sans ce controle, une dependance retiree casse l'entrainement sans que la porte le voie. |
| robustesse.perturbation | robustesse | Stabilité, bornes et champs optionnels | au plus 10 % de bascules sur 10 cas, bruit de 1 %; bornes et absences sans exception | 12 test(s) reussi(s) | conforme | Un bruit de mesure réaliste ne doit pas modifier massivement une décision; les limites et absences doivent rester explicites et sûres. |
| robustesse.determinisme | robustesse | Déterminisme de l'inférence | deux appels identiques donnent exactement le même résultat | 1 test(s) reussi(s) | conforme | Un score instable empêcherait toute analyse et toute reproductibilité de la décision. |
| robustesse.artefact_absent | robustesse | Refus propre d'un artefact manquant | FileNotFoundError explicite, sans prédiction dégradée silencieuse | 1 test(s) reussi(s) | conforme | Un moteur sans artefact ne doit jamais simuler un résultat ni échouer de façon ambiguë. |
| securite.bandit | sécurité | Analyse statique Bandit | 0 finding HIGH et 0 finding MEDIUM | 0 finding(s) HIGH/MEDIUM | conforme | Les sévérités HIGH et MEDIUM représentent un risque exploitable ou à traiter avant livraison; les LOW restent visibles dans le rapport Bandit. |
| securite.pip_audit | sécurité | Audit des dépendances Python | 0 vulnérabilité non acceptée | 0 vulnérabilité non acceptée (exception documentée: PYSEC-2026-2447) | conforme | L'avis sans correctif de diskcache est une exception temporaire et tracée dans docs/securite.md; toute autre vulnérabilité bloque la livraison. |
| securite.secrets_versionnes | sécurité | Absence de secret en clair versionné | aucun .env réel, secret/, .pem ou .key suivi par Git | aucun fichier sensible suivi | conforme | Une clé versionnée reste récupérable même après révocation; les exemples sans secret réel restent autorisés. |
| securite.401_sans_cle | sécurité | Refus sans clé d'API | POST /predict sans X-API-Key retourne 401 | HTTP 401 sans clé | conforme | L'absence d'authentification ne doit jamais donner accès au moteur de prédiction. |
| securite.entetes_owasp | sécurité | En-têtes HTTP de durcissement | CSP, anti-clickjacking, nosniff et referrer policy présents | 4/4 en-têtes attendus | conforme | Ces quatre en-têtes couvrent les protections web minimales revendiquées par l'application. |
