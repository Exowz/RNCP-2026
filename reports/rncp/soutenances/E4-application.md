# E4 — Développement d'une application intégrant un service d'IA

**Compétences C14 à C19 · 20 minutes · avec démonstration · troisième épreuve du passage**

Bandeau : `Compétences prouvées : Cx`. Rythme visé ~135 mots/minute.
**Budget : 14 min de présentation + 5 min de démonstration + 1 min de transition.**

> Les services tournent déjà depuis E3 — **ne rien relancer**. Vérifier seulement que les quatre répondent.

---

## Slide 1 — C14 : à qui sert cette application · 1 min 30

**Sur la slide**
> | Persona | Besoin | Ce qu'il reçoit |
> |---|---|---|
> | **Particulier informé** | Comprendre ce que les données permettent — et ne permettent pas — de conclure | Phrases, trois axes séparés, limites explicites |
> | **Analyste crédit** | Vérifier une donnée avant revue humaine | Règles, variables contribuant à l'écart, version du modèle |
> | **Exploitant technique** | Détecter un service indisponible ou dégradé | Sonde de santé, latence, taux d'erreur, identifiant de corrélation |
>
> **Hors périmètre assumé** : ni compte utilisateur, ni paiement, ni décision automatisée sur une personne, ni saisie d'adresse libre.

**Script**
> L'application sert trois publics, et le besoin de chacun est différent.
>
> Le particulier veut comprendre ce que les données permettent de conclure — et surtout ce qu'elles
> ne permettent pas. Il reçoit des phrases, pas des chiffres nus. L'analyste crédit veut vérifier
> une donnée avant une revue humaine : il reçoit les identifiants de règles, la décomposition de
> l'écart et la version du modèle. L'exploitant veut savoir si le service est dégradé.
>
> Et je définis explicitement un hors-périmètre : pas de compte utilisateur, pas de paiement, pas
> de décision automatisée sur une personne, pas de saisie d'adresse libre. Ce dernier point est un
> choix de minimisation : croiser une adresse précise, un prix et une étiquette énergétique permet
> de désigner un logement, donc potentiellement son occupant.

---

## Slide 2 — C14 : user stories et critères vérifiables · 1 min 30

**Sur la slide**
> | | User story | Critère d'acceptation **vérifiable** |
> |---|---|---|
> | **US-01** | savoir si un rapprochement est cohérent **sans** recevoir d'estimation de prix | trois axes affichés séparément ; **aucun** champ ni texte ne parle de prix |
> | **US-02** | connaître les inconnues avant de s'appuyer sur une réponse | réserves visibles ; DPE absent → « information insuffisante », pas une conclusion |
> | **US-04** | faire le parcours **sans souris ni couleur seule** | lien d'évitement, focus visible, `aria-live`, messages textuels |
> | **US-05** | une erreur compréhensible si l'API est indisponible | page 503 **sans trace interne**, marche à suivre expliquée |
> | **US-06** | relier une requête app à l'API | **même `X-Request-ID`** dans les journaux des deux services |

**Script**
> Six user stories, chacune avec un critère d'acceptation que je peux vérifier, pas une intention.
>
> Je m'arrête sur deux d'entre elles. La première dit que l'utilisateur veut savoir si un
> rapprochement est cohérent **sans** recevoir d'estimation de prix. Le critère est négatif et
> vérifiable : aucun champ, aucun texte ne parle de prix prédit. C'est une contrainte que je peux
> tester.
>
> La sixième est celle d'un exploitant : il veut pouvoir relier une requête de l'application à
> l'appel correspondant dans l'API. Le critère est le même identifiant de corrélation dans les deux
> journaux. Je vous montrerai que c'est le cas.

---

## Slide 3 — C15 : l'architecture réelle · 1 min 30

**Sur la slide**
> ```
> navigateur ──► Next.js :3000 ─┐                      ┌─► PostgreSQL :5433
>                               ├─► API modèle :8002 ──┤
> navigateur ──► Jinja   :8000 ─┘   └─► artefact local  └─► LM Studio :1234
>                                       concorde_moteur.pt      (service IA)
>                    └─────────────► API data :8001
> ```
> **La clé d'API ne quitte jamais le serveur.** Le navigateur ne parle qu'à son propre serveur.
> → aucun CORS à configurer, aucun secret dans le bundle JavaScript.
>
> **Contrainte structurante : hors ligne.** Garde-fou au niveau socket, pas une promesse.

**Script**
> Voici l'architecture réelle, pas un schéma générique.
>
> Deux clients, deux APIs, un artefact local, une base PostgreSQL et un service IA local. Le point
> que je veux souligner est le chemin de la clé d'API : le navigateur ne parle **jamais** aux ports
> Python. Il parle à son propre serveur, qui porte la clé et relaie l'appel.
>
> Cela a deux conséquences. Aucun secret ne se retrouve dans le bundle JavaScript — je l'ai vérifié
> en cherchant la clé dans les fichiers compilés, elle n'y est pas. Et il n'y a aucun CORS à
> configurer, puisqu'aucune requête n'est inter-origine.
>
> La contrainte qui a le plus structuré l'architecture, c'est le fonctionnement hors ligne. Et je ne
> me contente pas de le promettre : un garde-fou intercepte la couche socket et transforme toute
> sortie réseau non locale en erreur explicite. Une dépendance oubliée devient une erreur bruyante
> au développement, pas une surprise en soutenance.

---

## Slide 4 — C16 : le pilotage, et sa limite assumée · 1 min 15

**Sur la slide**
> **Ce que je montre** : kanban, backlog, **journal de décisions daté**, définition de « terminé », rétrospective.
> Chaque décision structurante : la décision · l'alternative écartée · **la raison**.
>
> **Ce que je n'ai pas** : rôles, rituels, animation collective. Je suis seul.
> **Je ne simule aucune équipe.** → C16 partiellement couverte, et je le dis.
>
> **Le volet MLOps de C16, lui, est entièrement couvert** : chaîne exécutée, artefact versionné, porte de conformité, incidents tracés.

**Script**
> Sur la coordination, je vais être direct, parce que c'est une limite et que je préfère l'annoncer
> moi-même.
>
> Le référentiel attend une conduite agile avec des rôles, des rituels et une animation collective.
> Je réalise ce projet seul. Je ne simule donc aucune équipe : ce serait la première chose qu'une
> question ferait tomber.
>
> Ce que je montre est réel : un kanban, un backlog, un journal de décisions daté où chaque choix
> structurant est consigné avec l'alternative écartée et la raison, une définition de « terminé »,
> et une rétrospective. La couverture collective de C16 est donc partielle, et je l'assume.
>
> En revanche, l'énoncé de C16 mentionne aussi un **contexte MLOps**, et cette moitié-là est
> entièrement couverte : chaîne exécutée, artefact versionné, porte de conformité, incidents tracés.

---

## Slide 5 — C17 : accessibilité, mesurée et non déclarée · 1 min 45

**Sur la slide**
> | Exigence | Réalisation | Vérification |
> |---|---|---|
> | Structure | `lang="fr"`, repères `header/nav/main/footer`, titres hiérarchisés | HTML servi |
> | Clavier | **lien d'évitement** en premier élément focusable, focus toujours visible | parcours sans souris |
> | Restitution | résultat annoncé en `aria-live="polite"`, erreurs en `role="alert"` | HTML servi |
> | **Contraste** | **calculé**, pas estimé | voir ci-dessous |
> | Adaptation | `prefers-reduced-motion`, pas de défilement horizontal < 320 px | media queries |
>
> **Contrastes mesurés — thème clair : 4,53 → 16,68:1 · thème sombre : 6,01 → 15,41:1** (seuil AA : 4,5)
> **Le sens n'est jamais porté par la seule couleur** : chaque état porte aussi un libellé.

**Script**
> L'accessibilité, maintenant, et je voudrais montrer la différence entre l'annoncer et la mesurer.
>
> La structure est sémantique, le premier élément focusable est un lien d'évitement, le résultat
> est annoncé aux lecteurs d'écran par une région `aria-live`, les erreurs par `role="alert"`.
>
> Mais le point sur lequel j'insiste, c'est le contraste. Je n'ai pas estimé « ça a l'air lisible » :
> j'ai calculé les ratios de luminance de chaque couple couleur-fond de ma palette, dans les deux
> thèmes. En thème clair, le plus serré est à 4,53 pour un seuil AA à 4,5. En thème sombre, le plus
> serré est à 6,01. Tout passe, et je peux vous montrer le calcul.
>
> Enfin, le sens n'est jamais porté par la seule couleur : un état « à vérifier » porte le mot « à
> vérifier », pas seulement une teinte orange. C'est le critère qui bénéficie le plus aux
> daltoniens, et c'est le plus souvent oublié.

---

## Slide 6 — C17 : sécurité applicative · 1 min 45

**Sur la slide**
```python
ENTETES_SECURITE = {
    "X-Content-Type-Options": "nosniff",        # A03 — pas d'inférence de type MIME
    "X-Frame-Options": "DENY",                  # A05 — pas de clickjacking
    "Referrer-Policy": "no-referrer",           # A01 — pas de fuite d'URL
    "Content-Security-Policy": "default-src 'self'; ...",  # A03 — aucune ressource distante
}
```
```python
for cle_connue, role in table.items():
    if secrets.compare_digest(x_api_key, cle_connue):   # temps constant
        role_trouve = role
```
> **Rôles** `reader` / `analyst` / `admin` · **secrets hors Git** · **journaux pseudonymisés à l'écriture**
> **`import "server-only"`** : le build **échoue** si un composant client importe le module portant la clé.

**Script**
> Sur la sécurité, quatre mécanismes, chacun rattaché à un risque OWASP identifié.
>
> Les en-têtes de durcissement, posés sur toutes les réponses. La politique de sécurité du contenu
> interdit toute ressource distante — ce qui est aussi ma contrainte hors ligne, les deux se
> renforcent.
>
> La comparaison des clés se fait à **temps constant**. Une comparaison naïve s'arrête au premier
> caractère différent, et la durée de réponse fuit alors la clé, caractère par caractère. C'est une
> attaque réelle, et la parade tient en une fonction.
>
> Les journaux pseudonymisent les champs personnels **avant** l'écriture sur disque, pour qu'un
> fichier de log ne devienne pas une base de données personnelles clandestine.
>
> Et le dernier, dont je suis satisfait : `import "server-only"` en tête du module qui porte la clé
> d'API. Ce n'est pas une convention, c'est une garantie mécanique : si un développeur importe ce
> module depuis un composant client, **le build échoue**. Il est impossible de faire fuiter la clé
> par inadvertance.

---

## Slide 7 — C18 : les tests automatisés au versionnement · 1 min 15

**Sur la slide** — capture `reports/captures/04-ci-github-verte.png`
> Déclenchée à **chaque poussée**. 17 étapes, dont :
> `pytest` (51 tests) · `ruff` · **`bandit`** (0 HIGH/MEDIUM) · **`pip-audit`** (0 vulnérabilité) · **porte de conformité** · `uv build`
>
> **La sécurité n'est pas relue à la main : elle est vérifiée à chaque commit.**
> `pip-audit` = OWASP **A06 — composants vulnérables et obsolètes**.

**Script**
> L'intégration continue se déclenche à chaque poussée et enchaîne dix-sept étapes.
>
> Au-delà des tests et du lint, j'ai branché deux contrôles de sécurité. Bandit, qui fait l'analyse
> statique du code Python et cherche les motifs dangereux. Et pip-audit, qui compare mon graphe de
> dépendances à une base d'avis de sécurité publiés.
>
> Ce second contrôle correspond exactement à l'entrée A06 de l'OWASP Top 10 : composants vulnérables
> et obsolètes. Et il a servi : il a détecté deux vulnérabilités réelles dans mes dépendances, dont
> une corrigeable. J'y reviens dans la dernière épreuve, parce que c'est devenu un incident documenté.
>
> Le point important : la sécurité n'est pas une relecture ponctuelle, c'est une vérification
> automatique à chaque commit.

---

## Slide 8 — C19 : la livraison, conditionnelle · 1 min 30

**Sur la slide**
> ```
> commit ──► tests ──► lint ──► bandit ──► pip-audit ──► [PORTE] ──► build ──► artefact
>                                                            │
>                                                            └─ 1 critère bloquant échoue → code 1 → rien n'est construit
> ```
> **Image Docker locale** `concorde:local` · démarrage `docker compose --no-build` · sonde `healthy`
> Paquet publié : roue + archive source + **modèle gelé** + fiche + métriques.
>
> **Livraison conditionnelle, pas automatique.**

**Script**
> La livraison, enfin. Le processus produit un paquet Python et une image Docker, tous deux
> disponibles localement — l'image est déjà construite, la démonstration ne télécharge rien.
>
> Mais l'élément que je veux souligner, c'est la position de la porte de conformité : **avant** la
> construction. Douze critères de qualité, robustesse et sécurité sont évalués, et si un seul
> critère bloquant échoue, le script sort en code non nul et rien n'est construit.
>
> C'est ce qui fait la différence entre une chaîne qui teste et une chaîne qui **décide**. La
> livraison est conditionnelle : elle n'a lieu que si le système se déclare conforme, et ce verdict
> est calculé, pas rédigé.

---

## Slide 9 — Transition vers la démonstration · 30 s

**Sur la slide**
> **Démonstration — le parcours utilisateur complet, et ce qui se passe quand ça casse**

**Script**
> Je passe à la démonstration de l'application. Je vais montrer le parcours d'un particulier, la
> bascule vers la lecture analyste, l'accessibilité au clavier, et enfin le comportement quand le
> service tombe.

---

## DÉMONSTRATION · 5 minutes

### D1 · Le parcours et sa lisibilité — 1 min 30
**Faire** : `http://127.0.0.1:3000/` — rester sur l'accueil, faire défiler lentement

> **Dire** : « La première chose que voit l'utilisateur n'est pas un formulaire, c'est le problème :
> deux bases publiques décrivent le même logement sans identifiant commun, le rapprochement peut
> être faux, et rien ne le signale.
>
> Juste en dessous, le vocabulaire est défini — DVF+, DPE, rapprochement — parce qu'aucune
> connaissance préalable n'est attendue de l'utilisateur. Et l'avertissement est permanent :
> Concorde n'estime aucun prix.
>
> Les cinq cas proposés sont extraits de la table réelle. Vous voyez les noms de communes, les
> étiquettes énergétiques sur leur échelle, les dates en clair — pas des identifiants de base de
> données. »

### D2 · Les trois axes et l'échelle — 1 min 15
**Faire** : cliquer **« Surfaces DVF et DPE incompatibles »**

> **Dire** : « Les trois axes, et chacun porte son échelle. "100 % signifie qu'aucune contradiction
> connue n'a été détectée. Ce score ne mesure pas le prix du logement." Un pourcentage nu ne veut
> rien dire ; celui-ci est accompagné de sa lecture.
>
> Et la section "Pourquoi ce résultat ?" donne le motif en français, avec sa gravité — pas un code
> d'erreur. »

### D3 · L'accessibilité, au clavier — 1 min
**Faire** : recharger, puis **Tab** une fois → le lien d'évitement apparaît ; **Tab** plusieurs fois

> **Dire** : « L'accessibilité se démontre, elle ne se déclare pas. Je recharge, j'appuie une fois
> sur Tab : le premier élément focusable est le lien d'évitement, qui permet d'atteindre le contenu
> sans traverser la navigation. Il est invisible jusqu'au focus clavier.
>
> Je continue : chaque élément reçoit un contour de focus visible et contrasté. Tout le parcours se
> fait sans souris. »

### D4 · Ce qui se passe quand ça casse — 1 min 15
**Faire** : terminal → `pkill -f "uvicorn api.model.main"` → recharger la page de résultat

> **Dire** : « Et voici le cas qui compte le plus. J'arrête l'API du modèle et je recharge.
>
> L'application n'affiche ni page blanche, ni trace technique, ni erreur 500. Elle affiche
> "Résultat indisponible", avec un message compréhensible, annoncé aux lecteurs d'écran par
> `role="alert"`. Aucun résultat partiel n'est présenté : **en cas de panne, l'application préfère
> ne rien avancer plutôt qu'avancer quelque chose d'invalide.**
>
> C'est un comportement conçu et couvert par un test, pas un heureux hasard. »

**Faire** : relancer l'API pour la suite
```bash
.venv/bin/uvicorn api.model.main:app --host 127.0.0.1 --port 8002 &
```

---

## Slide 10 — Récapitulatif E4 · 45 s

**Sur la slide**

| | Preuve | Où |
|---|---|---|
| **C14** | 3 personas, 6 user stories à **critères vérifiables**, exigences WCAG/RGAA | `docs/specs-fonctionnelles.md` |
| **C15** | Architecture réelle, flux, clé jamais côté navigateur, garde-fou hors ligne | `docs/architecture.md` |
| **C16** | Kanban, journal daté, DoD, rétro — **collectif partiel assumé**, MLOps complet | `docs/pilotage.md` |
| **C17** | OWASP (4 en-têtes, temps constant, `server-only`) · **contrastes calculés** | `docs/securite.md` |
| **C18** | CI à chaque poussée + **bandit** + **pip-audit** | run public |
| **C19** | Image Docker locale, `--no-build`, **porte bloquante avant build** | `docs/livraison.md` |

**Script**
> Pour résumer : un besoin analysé avec des critères vérifiables, une architecture où le secret ne
> quitte jamais le serveur, une accessibilité mesurée et pas déclarée, une sécurité rattachée à
> l'OWASP et vérifiée automatiquement, et une livraison conditionnée à une porte de conformité.
>
> Et une limite assumée sur la coordination collective, parce que je suis seul.
>
> Je passe au choix et à la configuration du service d'intelligence artificielle.

---

## Aide-mémoire

**Vérifier avant de partager l'écran**
```bash
for p in 8001/sante 8002/sante 8000/ 3000/; do
  curl -so /dev/null -w "$p -> %{http_code}\n" http://127.0.0.1:${p}
done
```

**Après la démonstration D4, ne pas oublier de relancer l'API modèle.**

**Questions probables**
- *Pourquoi deux applications ?* → prouver que l'API est un contrat, pas un utilitaire de gabarit ; deux clients indépendants la consomment en HTTP.
- *Votre accessibilité est-elle auditée ?* → les critères sont vérifiés et les contrastes calculés ; un audit RGAA certifié par un tiers reste à faire, je ne le revendique pas.
- *Comment gérez-vous les secrets ?* → hors Git, chargés depuis l'environnement, jamais préfixés `NEXT_PUBLIC` ; et `server-only` fait échouer le build si la règle est violée.
- *Le profil change-t-il le résultat ?* → jamais. Il change la restitution. Deux utilisateurs voyant deux chiffres différents sur la même donnée serait un défaut de conception.
