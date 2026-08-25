# Benchmark des services IA existants — C7

## Besoin IA reformulé

### Contexte métier

Concorde signale des incohérences possibles entre DVF+, DPE et Géorisques. Son
verdict reste volontairement prudent : l’objectif n’est ni d’estimer un prix ni
de décider à la place d’un utilisateur. Un particulier peut cependant avoir
besoin d’une lecture plus simple des motifs et réserves déjà calculés.

### Entrées

Le service de reformulation reçoit exclusivement une projection du verdict :
statut, niveau d’anomalie, score de cohérence, motifs, confiance, réserves et
texte assemblé. Il ne reçoit ni adresse, ni parcelle, ni mutation, ni DPE brut,
ni identité.

### Sorties

Il retourne une ou deux phrases de français courant, identifiées
`modele_local`. Lorsqu’il est indisponible, Concorde retourne le texte assemblé
existant, identifié `texte_assemble`. Les scores, motifs et réserves restent
affichés tels que calculés, à côté de cette aide de lecture.

### Contraintes

| Sujet | Contrainte vérifiable |
|---|---|
| Coût | Aucun coût variable ni compte tiers : modèle déjà chargé sur le poste. |
| Latence | Délai HTTP de 3 secondes ; la prédiction ne dépend pas de cette route. Le prévol réchauffe le modèle chargé avec TTL d’une heure. |
| Sécurité | Boucle locale, rôle `reader`, contrat strict, sortie bornée et rendue comme texte React. |
| RGPD | Pas de donnée brute, adresse, parcelle ou identifiant transmis au LLM ; aucune requête Internet. |
| Local / cloud | Démonstration hors ligne sur `127.0.0.1`; les API cloud sont exclues. |
| Accessibilité | Le texte est lisible, annoncé dans la zone de résultat et complété par une provenance explicite. |

### Critères de réussite

1. le texte améliore la lecture sans calculer ni modifier une décision ;
2. la dégradation renvoie le texte assemblé sans erreur visible ;
3. la CI couvre le service absent sans exiger LM Studio ;
4. l’appel local est borné, mesuré et traçable ;
5. aucun secret, contenu HTML non fiable ou appel cloud n’atteint le navigateur.

## Comparaison

| Service | Fonctionnel | Technique | Risque | Décision |
|---|---|---|---|---|
| **LM Studio + Gemma 4B** | Rédige une phrase à partir d’une consigne choisie par le code, sans interpréter le verdict. | API HTTP locale `127.0.0.1`; `google/gemma-4-e4b` réchauffé; `temperature=0`, 90 tokens, délai 3 s. | Gemma 4/MLX fuit parfois son raisonnement ou dépasse le délai : 2 réponses acceptées sur 3 mesures chaudes; le repli est compté et les éléments calculés restent visibles. | **Retenu sous garde-fou** : capacité locale réelle, mais aucune réponse non conforme n’est affichée. |
| Ollama | Capacité de reformulation comparable. | Local possible mais non installé et sans modèle chargé. | Télécharger et dupliquer un poids ajoute temps, stockage et une dépendance de démonstration. | Écarté : aucune valeur fonctionnelle supplémentaire face à LM Studio prêt localement. |
| API LLM cloud | Reformulation de qualité possiblement élevée. | Réseau, clé fournisseur et disponibilité d’un tiers. | Transfert de prompts, coût variable, indisponible hors ligne et mauvaise démonstration RGPD. | Écarté : contredit directement les contraintes de Concorde. |
| Modèle scikit-learn interne | Évalue l’anomalie, la cohérence et la confiance. | Autoencodeur PyTorch local déjà présent. | Le détourner en générateur de texte confondrait calcul du verdict et restitution. | Écarté pour la reformulation : il reste seul responsable du calcul. |

Une reformulation libre a observé une inversion de sens (« cohérent » malgré une
contradiction majeure) après 31,6 s et 551 tokens. Cette observation élimine le
LLM comme interprète du verdict. Le choix retenu ne lui confie que la rédaction
d’une consigne déterminée par le code; le texte assemblé reste la référence et
le taux de repli une métrique de fiabilité.
