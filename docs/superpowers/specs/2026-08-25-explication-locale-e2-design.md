# Explication locale du verdict — conception E2

## Intention

Concorde utilise un service IA local uniquement pour améliorer la lisibilité d’un verdict déjà calculé, pour le profil particulier. Il ne l’emploie ni pour produire, ni pour modifier, ni pour arbitrer une décision.

## Limites de responsabilité

`POST /predict` et le moteur de décision restent inchangés, rapides et déterministes. Une nouvelle route authentifiée `POST /expliquer` reçoit une projection stricte du verdict : statut, niveau d’anomalie, score de cohérence, motifs, confiance, réserves et texte assemblé. Elle exclut toute donnée brute de mutation ou de DPE, toute adresse et tout identifiant de parcelle.

Le code transforme cette projection en une consigne rédactionnelle déterministe
avant l’appel. Le service LM Studio ne reçoit donc aucun score, motif ou réserve
à interpréter : seulement la phrase factuelle qu’il doit rédiger. Les scores,
motifs et réserves calculés continuent à être affichés tels quels par le client,
à côté de ce texte.

## Contrat et dégradation

La route est réservée au rôle `reader` et répond :

```json
{ "texte": "…", "source": "modele_local" }
```

ou, si LM Studio est indisponible, en erreur ou renvoie une réponse invalide :

```json
{ "texte": "<explication assemblée validée>", "source": "texte_assemble" }
```

La dégradation est une réponse 200 : elle est le comportement normal lorsque le service local optionnel n’est pas lancé. Le client Next.js appelle la route depuis son Server Component, avec `CONCORDE_API_KEY`; aucune clé ni requête vers le port Python ne parvient au navigateur.

## Défense en profondeur

- LM Studio est appelé avec `temperature=0`, un délai de 3 secondes et au plus 90 tokens. Toute sortie avec raisonnement, `finish_reason` différent de `stop` ou moins de 15 caractères est rejetée.
- Une réponse LLM est tronquée à 1 000 caractères côté API, même si le serveur local ne respecte pas le plafond demandé.
- Le front rend ce contenu dans un nœud React textuel, sans Markdown et sans `dangerouslySetInnerHTML`; React l’échappe donc avant affichage.
- La provenance est explicitement visible sous le texte. L’utilisateur peut comparer la reformulation avec les éléments calculés qui restent à l’écran.
- Chaque tentative locale écrit sa latence, son statut, son succès ou son repli dans `monitoring/model/metriques_lm_studio.json`.

## Preuves E2

Un test non marqué force l’indisponibilité de LM Studio et vérifie le repli sur le texte assemblé. Un test `local_service` couvre l’appel réel lorsque LM Studio est lancé, sans devenir une dépendance de CI. La documentation de veille, benchmark et pilotage apporte séparément les éléments C6, C7 et C8.

## Hors périmètre

Le moteur (`src/concorde/model/**`), l’application Jinja, l’API data, la porte de conformité et le workflow CI ne changent pas. L’API modèle et son contrat, le client de service, les tests associés, le client Next.js et les documents E2 sont les seules surfaces modifiées.
