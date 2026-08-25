# Service IA local LM Studio — C8

Service retenu : LM Studio, API OpenAI-compatible liée à `127.0.0.1:1234`.
Modèle : `google/gemma-4-e4b`, présent localement. Le serveur est lié à la
boucle locale : aucune donnée Concorde ne part sur Internet.

## Démarrage et vérification

```bash
~/.lmstudio/bin/lms load google/gemma-4-e4b
~/.lmstudio/bin/lms server start
curl http://127.0.0.1:1234/v1/models
source scripts/spark-env.sh
.venv/bin/python -m pytest tests/model/test_lm_studio_service.py -m local_service -q
```

La configuration Concorde se trouve dans `.env.example` :

```dotenv
CONCORDE_LM_STUDIO_URL=http://127.0.0.1:1234/v1
CONCORDE_LM_STUDIO_MODEL=google/gemma-4-e4b
```

## Travail confié au service

`POST /expliquer` reçoit un verdict déjà calculé et produit une aide de lecture
pour la restitution « particulier ». Il est séparé de `POST /predict` : le
moteur garde seul la décision, les scores, les motifs et les réserves.

Le code lit la projection pour choisir une consigne de rédaction déterministe —
par exemple « contradiction majeure détectée, vérification nécessaire ». Le LLM
ne reçoit ni JSON de verdict, ni score, ni motif à interpréter : seulement cette
consigne courte. Il ne reçoit donc ni mutation, ni DPE brut, ni adresse, ni
parcelle, ni identifiant. L’instruction demande une phrase de 20 mots maximum,
sans chiffre, HTML ni Markdown.

La réponse porte une provenance : `modele_local` si la reformulation réussit,
`texte_assemble` si le service local est absent, en erreur ou renvoie un texte
invalide. Dans ce second cas, l’API renvoie l’explication assemblée par le moteur
sans afficher d’erreur au particulier. Le texte additionnel ne remplace jamais
les scores, motifs ou réserves qui restent visibles dans l’interface.

## Paramètres et monitorage

| Paramètre | Valeur | Justification |
|---|---:|---|
| `temperature` | `0` | Réduit la variabilité d’une reformulation qui ne doit pas créer de contenu. |
| `max_tokens` | `90` | Suffit pour une phrase de 20 mots et limite la durée comme la surface de contenu non fiable. |
| Délai HTTP | `3 s` | La fonction est optionnelle : au-delà, le repli immédiat est préférable à l’attente. |
| Taille de sortie | `1 000` caractères | Borne appliquée de nouveau côté API, même si le serveur local ne respecte pas le plafond demandé. |

Le code refuse la sortie dès qu’elle dépasse le délai, que le statut HTTP échoue,
que `finish_reason` diffère de `stop`, que `reasoning_tokens` est non nul, que
`reasoning_content` est présent ou que le texte contient moins de 15 caractères.
Chaque tentative de `/v1/chat/completions` mesure statut et latence, incrémente
`appels_reformulation`, puis `reformulations_modele_local` ou
`replis_texte_assemble` et `erreurs_reformulation`. L’instantané est écrit dans
`monitoring/model/metriques_lm_studio.json`. Le test non marqué
`test_expliquer_replie_sur_texte_assemble_si_lm_studio_est_absent` garantit le
parcours dégradé en CI ; le test réel LM Studio reste marqué `local_service`.

## Mesures et limite du modèle retenu

Les mesures du 25 août sur Gemma 4 E4B / moteur MLX ont révélé que l’option de
raisonnement ne se désactive pas de façon fiable par requête :
`reasoning_effort=none` affiche la chaîne de raisonnement dans `content`,
`reasoning_effort=low`, `reasoning:{enabled:false}` et
`chat_template_kwargs:{enable_thinking:false}` ne la suppriment pas. Une
reformulation libre a consommé 551 tokens en 31,6 s; elle a même inversé le sens
d’un verdict à 60 % de cohérence avec contradiction majeure.

La consigne de rédaction courte a donné trois mesures chaudes : 3,8 s, 1,2 s et
un échec, soit deux réponses acceptées sur trois. Le démarrage à froid explique
une part de la variabilité : 18,9 s, puis 8,5 s, puis 0,34 s pour une requête
triviale. Le prévol charge donc `google/gemma-4-e4b` avec un TTL d’une heure,
démarre le serveur, puis vérifie `lms ps` avant la démonstration.

Le taux de repli est une métrique attendue, pas un défaut caché : le texte
assemblé reste la réponse de référence et une source `modele_local` ne paraît
que lorsque tous les contrôles ci-dessus passent. Le bug du moteur MLX est suivi
dans l’[issue LM Studio #337](https://github.com/lmstudio-ai/mlx-engine/issues/337).

## Restitution sûre

La sortie d’un modèle local reste du contenu non fiable. Le client web la rend
dans un nœud texte React, sans conversion Markdown ni HTML et sans
`dangerouslySetInnerHTML`. React l’échappe avant affichage. La provenance
affichée rend la nature optionnelle de cette aide de lecture vérifiable.
