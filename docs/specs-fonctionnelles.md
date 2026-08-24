# Spécifications fonctionnelles — C14

## Besoin et périmètre

Concorde aide à évaluer la **fiabilité d'un rapprochement** entre une mutation
DVF+, un DPE ADEME et le niveau d'aléas Géorisques de la commune. Il ne prédit
ni prix, ni valeur vénale, ni tarif ; il ne prend aucune décision à la place de
l'utilisateur.

Le produit est une démonstration locale hors ligne. Les scénarios sont issus de
fixtures versionnées : ils sont reproductibles, mais ne prétendent pas décrire
le parc immobilier français.

## Utilisateurs et parcours

| Persona | Besoin principal | Parcours | Information rendue |
|---|---|---|---|
| Particulier informé | Comprendre ce que les données permettent — et ne permettent pas — de conclure. | Choisit un cas, lance l'évaluation, lit les réserves. | Phrases simples, trois axes séparés, limites explicites. |
| Analyste crédit | Vérifier une donnée avant revue humaine. | Choisit la lecture analyste, évalue un cas, consulte motifs et variables atypiques. | Règles, variables contribuant à l'écart, version du modèle. |
| Exploitant technique | Détecter un service indisponible ou dégradé. | Appelle `/sante`, puis consulte les métriques locales. | État de l'API amont, latence, taux d'erreur, identifiant de corrélation. |

Le profil de lecture ne modifie jamais l'algorithme ni le verdict : il adapte
seulement le niveau de détail affiché. Cette séparation évite qu'un même
rapprochement reçoive deux conclusions différentes selon le public.

## User stories et critères d'acceptation

| ID | User story | Critères d'acceptation vérifiables |
|---|---|---|
| US-01 | En tant que particulier, je veux savoir si un rapprochement est cohérent sans recevoir une estimation de prix. | La page résultat affiche cohérence, atypicité et confiance séparément ; aucun champ ni texte ne parle de prix prédit ou de tarification. |
| US-02 | En tant que particulier, je veux connaître les inconnues avant de m'appuyer sur une réponse. | Les réserves de confiance sont visibles ; un DPE absent produit « information insuffisante » plutôt qu'une conclusion affirmative. |
| US-03 | En tant qu'analyste, je veux voir pourquoi un cas est signalé. | Les motifs de contradiction, leur gravité et les variables atypiques sont affichés dans la lecture analyste. |
| US-04 | En tant qu'utilisateur clavier ou lecteur d'écran, je veux effectuer le parcours sans souris ni couleur seule. | Lien d'évitement, ordre de titres, libellés de radios, focus visible, résultat `aria-live`, tableau avec en-têtes et messages textuels sont présents. |
| US-05 | En tant qu'utilisateur, je veux une erreur compréhensible si l'API modèle est indisponible. | Le POST affiche une page 503 sans trace interne et explique la marche locale à suivre. |
| US-06 | En tant qu'exploitant, je veux relier une requête app à l'API. | Le même `X-Request-ID` apparaît dans les logs JSONL des deux services. |

## Exigences d'utilisabilité et d'accessibilité

La cible est WCAG 2.1 niveau AA, traduite en contrôles RGAA directement
vérifiables dans le HTML produit.

| Exigence | Réalisation dans Concorde |
|---|---|
| Structure compréhensible | `lang=fr`, un `main`, titres hiérarchisés, navigation nommée, fil d'Ariane. |
| Clavier | Lien d'évitement en premier, tous les contrôles natifs, focus à contraste renforcé, aucun piège clavier. |
| Formulaire | `fieldset`, `legend`, labels associés aux radios et texte d'aide référencé par `aria-describedby`. |
| Restitution | Le résultat est annoncé par `aria-live="polite"`; aucune information ne dépend de la seule couleur. |
| Contraste et adaptation | Palette documentée à 4,5:1 minimum ; média `prefers-contrast` et `prefers-reduced-motion`; lecture sans défilement horizontal sur petit écran. |
| Contenu compréhensible | Vocabulaire « ce qui se contredit » / « ce que l'on ne sait pas », puis détails techniques réservés au profil analyste. |

## Hors périmètre assumé

Il n'y a ni compte utilisateur, ni paiement, ni décision automatisée sur une
personne, ni interface de saisie d'adresse libre. Ces choix réduisent le risque
de ré-identification et concentrent la démonstration sur la qualité des
données. Un audit avec des utilisateurs réels et un audit RGAA certifié restent
à faire hors de l'évaluation.
