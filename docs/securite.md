# Sécurité et gestion des accès — C17

## Modèle de menace proportionné

Concorde est une démonstration locale : le risque principal est l'exposition
accidentelle d'une API, d'un secret, d'une donnée de rapprochement ou d'une
dépendance réseau. Il n'y a ni compte Internet, ni paiement, ni donnée de
personne enregistrée dans PostgreSQL.

| Risque OWASP / opérationnel | Mesure implémentée | Preuve |
|---|---|---|
| API métier accessible sans contrôle | `X-API-Key`, rôles `reader` / `analyst` / `admin`, 401 et 403. | `tests/api/test_api_data.py`, `tests/api/test_api_modele.py`. |
| Comparaison de clé exploitable par le temps | `secrets.compare_digest` sur toutes les clés connues. | `src/concorde/service/securite.py`. |
| Entrée inattendue / injection de contrat | Schémas Pydantic stricts ; champ inconnu refusé en 422. | Test `test_predict_rejette_un_champ_inconnu`. |
| Fuite de secrets ou de données dans Git | `.env` ignoré, `.env.example` sans secret, clés lues depuis l'environnement. | `.gitignore`, `common/config.py`. |
| XSS, clickjacking, MIME-sniffing | CSP sans ressource distante, `X-Frame-Options: DENY`, `nosniff`, politique de référent. | `EntetesSecuriteMiddleware`. |
| Dépendance Internet dissimulée | Garde-fou socket, seuls les hôtes loopback sont permis. | Tests app/API hors ligne. |
| Ré-identification dans les logs | IP et clé pseudonymisées avant écriture JSONL ; pas d'adresse complète. | `logging_setup.py`, registre RGPD. |

## Droits et flux d'accès

Les APIs data et modèle sont des services internes. Une clé de rôle `reader`
permet la lecture/prediction ; `analyst` donne accès aux métriques et au lot ;
`admin` est réservé aux opérations futures. Les routes `/sante` restent sans
clé pour permettre les sondes de démarrage, mais ne divulguent ni données ni
secrets.

L'application web ne reçoit pas de compte utilisateur : elle est servie en
local et son profil « particulier / analyste » est une **vue de restitution**,
pas une élévation de privilège. Les détails analyste n'ajoutent aucune donnée
personnelle et la décision du modèle reste identique.

## Accessibilité livrée avec l'interface

La sécurité ne se fait pas au détriment de l'accès : l'interface utilise des
contrôles HTML natifs, labels associés, lien d'évitement, focus visible,
structure de titres, contraste documenté, messages d'erreur explicites et
résultat annoncé par lecteur d'écran. Les détails sont vérifiables dans
`docs/specs-fonctionnelles.md` et les templates `app/templates/`.

## Limites et amélioration nécessaire

Les clés de démonstration sont des valeurs locales, pas une gestion d'identité
pour un service public. Avant toute exposition réseau réelle, il faudrait :
TLS, rotation et stockage dédié des secrets, limitation de débit persistante,
authentification utilisateur, journal d'audit protégé et revue de sécurité.
Ces absences sont assumées car elles dépassent le périmètre de la démo hors
ligne ; elles ne sont pas cachées derrière les clés API de développement.

## Audit des dépendances — 2026-08-25

La porte `scripts/conformite.py` et la CI exécutent Bandit ainsi que
`pip-audit`. Le 25 août, l'audit a trouvé `cryptography 49.0.0`
(`PYSEC-2026-3552`) et `diskcache 5.6.3` (`PYSEC-2026-2447`). Le premier avis
est corrigé par le verrou `cryptography 50.0.0`. La distribution complète de
MLflow plafonnait toutefois `cryptography<50` ; elle est remplacée par
`mlflow-skinny 3.15.1`, qui couvre le tracking SQLite réellement utilisé par
Concorde sans embarquer le serveur et l'UI inutilisés.

`diskcache` est une dépendance transitive de `dvc-data`, elle-même requise par
DVC 3.67.1. L'avis ne liste aucun correctif. L'exception
`PYSEC-2026-2447` est donc temporairement explicitée et limitée à cette seule
référence dans la commande d'audit ; toute autre vulnérabilité reste bloquante.
Elle sera réexaminée à chaque mise à jour DVC et au plus tard le 2026-09-25.
Cette exception ne change ni le rapport brut de `pip-audit`, ni le fait que le
critère de conformité compte **zéro vulnérabilité non acceptée**.
