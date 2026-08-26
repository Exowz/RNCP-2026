# E5 — Monitorage applicatif et résolution d'incident

**Compétences C20 et C21 · 10 minutes · dernière épreuve du passage**

Bandeau : `Compétences prouvées : Cx`. Rythme visé ~135 mots/minute.
**C'est la dernière chose que le jury entendra avant ses questions.** Finir sur les incidents.

> ⏱ **Marge serrée : 9,6 min mesurées sur 10.** Si tu es en retard en arrivant ici, **saute la
> slide 5 bis** (« quand le poste ment »). Elle est excellente mais c'est la seule dont l'absence
> ne coûte rien : les deux incidents détaillés restent, et la slide 4 les mentionne tous les cinq.
> **Ne sacrifie jamais la slide 7** — c'est ta conclusion.

---

## Slide 1 — C20 : ce que je journalise, et ce que je refuse de journaliser · 1 min 30

**Sur la slide**
```python
SENSIBLES = {"adresse", "nom", "email", "telephone", "ip", "api_key", "password", "token"}

class RgpdRedactionFilter(logging.Filter):
    """Masque les champs personnels AVANT la serialisation."""
    def filter(self, record):
        for cle in vars(record):
            if cle.lower() in SENSIBLES:
                setattr(record, cle, pseudonymize(getattr(record, cle)))  # SHA-256 tronqué
        return True
```
> Format **JSON Lines** — exploitable par `jq`, sans parser du texte libre.
> La pseudonymisation a lieu **avant l'écriture disque** : un fichier de log ne doit jamais devenir
> une base de données personnelles clandestine.

**Script**
> Le monitorage applicatif, et je commence par ce que je refuse de journaliser.
>
> Les journaux sont au format JSON Lines : une ligne JSON par événement, exploitable directement
> avec `jq`, sans parser du texte libre et fragile.
>
> Mais le point important est le filtre de pseudonymisation. Les champs identifiés comme personnels
> — adresse, nom, email, adresse IP, clé d'API — sont remplacés par une empreinte SHA-256 tronquée
> **avant** l'écriture sur disque. Pas après, pas à la lecture : avant.
>
> La raison est directe. On protège soigneusement une base de données, et on laisse les mêmes
> informations s'accumuler en clair dans les journaux pendant des mois. Un fichier de log ne doit
> jamais devenir une base de données personnelles clandestine. L'empreinte permet quand même de
> compter, de corréler et de dédupliquer, sans stocker la donnée elle-même.

---

## Slide 2 — C20 : la corrélation de bout en bout · 1 min 15

**Sur la slide**
> Un `X-Request-ID` traverse **application → API → moteur**, porté par un `ContextVar`.
>
> ```
> app.jsonl        {"request_id":"a3f2…","event":"evaluation","route":"/evaluer"}
> api-model.jsonl  {"request_id":"a3f2…","event":"prediction","niveau_anomalie":"a_verifier"}
> ```
> → un incident se rejoue en filtrant sur **un seul identifiant**.
>
> ```bash
> jq 'select(.request_id=="a3f2…")' monitoring/logs/*.jsonl
> ```

**Script**
> Deuxième brique : la corrélation.
>
> Chaque requête reçoit un identifiant, propagé par une variable de contexte à travers
> l'application, l'appel HTTP à l'API, et la prédiction. Le même identifiant apparaît donc dans les
> journaux des deux services.
>
> La conséquence pratique est celle-là : quand un utilisateur signale un comportement anormal, je
> n'ai pas à recouper des horodatages entre deux fichiers. Je filtre sur un identifiant et j'obtiens
> la trace complète de sa requête, de son clic jusqu'au verdict.
>
> C'est ce qui transforme un incident en quelque chose de rejouable plutôt qu'en enquête.

---

## Slide 3 — C20 : seuils, alertes, tableau de bord · 1 min 15

**Sur la slide** — capture `reports/captures/04-surveillance-locale-seuils-alertes.jpg`
> **Mesuré par route** : appels · erreurs client (4xx) · erreurs serveur (5xx) · latence p50 / p95 / max
>
> | Seuil | Valeur | Sévérité |
> |---|---|---|
> | Latence p95 | > **750 ms** | avertissement |
> | Taux d'erreur | > **5 %** | critique |
>
> **Évalués à partir de 5 appels** sur une même route — on n'alerte pas sur un point unique.
> Restitution : page `/exploitation`, en local, **aucune métrique envoyée à un service externe**.

**Script**
> Troisième brique : les seuils et les alertes.
>
> Pour chaque route, je mesure les appels, les erreurs client, les erreurs serveur, et les latences
> en p50, p95 et maximum sur une fenêtre glissante.
>
> Deux seuils déclenchent des alertes : un p95 au-dessus de 750 millisecondes en avertissement, un
> taux d'erreur au-dessus de 5 % en critique. Et une précaution qui compte : ils ne sont évalués
> qu'à partir de cinq appels sur une même route. Alerter sur un échantillon d'un seul point produit
> du bruit, et une alerte qui crie pour rien finit par être ignorée.
>
> Le tout est restitué sur une page locale. Aucune métrique n'est envoyée à un service externe :
> c'est cohérent avec la contrainte hors ligne et avec le registre RGPD.

---

## Slide 4 — C21 : cinq incidents réels · 1 min 30

**Sur la slide**

| Identifiant | Nature | Ce qu'il enseigne |
|---|---|---|
| `CI-2026-08-24` | ordre d'initialisation PostgreSQL, puis packaging incomplet | un lancement local masque une erreur de packaging |
| `APP-2026-08-25` | la bascule de profil renvoyait **405** en pleine démonstration | un lien relatif suppose le verbe HTTP de la page |
| `CI-2026-08-25` | tests **verts en local, rouges en CI** (503) | le poste fournissait silencieusement un service démarré |
| `SEC-2026-08-25` | **2 dépendances vulnérables** détectées par la porte | la chaîne d'approvisionnement s'audite, ne se suppose pas |
| `SEC-2026-08-25-bis` | la porte déclarait **conforme une chaîne cassée** | un artefact valide ne prouve que le passé |

> **Chacun** : reproduction · diagnostic · correctif minimal · non-régression **vérifiée dans les deux sens** · REX.

**Script**
> Sur la résolution d'incident, je n'ai pas eu à en provoquer un : le projet m'en a fourni cinq,
> tous réels, tous documentés.
>
> Le premier vient de l'intégration continue : un ordre d'initialisation erroné, puis un défaut de
> packaging. Le deuxième cassait ma propre démonstration : un clic sur le sélecteur de profil
> renvoyait une erreur 405 en JSON brut. Le troisième est le plus instructif sur la méthode. Le
> quatrième vient de la porte de conformité, qui a détecté deux vulnérabilités réelles dans mes
> dépendances. Et le cinquième porte sur l'outil de contrôle lui-même.
>
> Chacun suit la même discipline : reproduction, diagnostic, correctif minimal, test de
> non-régression vérifié **dans les deux sens**, et retour d'expérience.
>
> Je vais en détailler deux.

---

## Slide 5 — C21 : l'incident qui cassait la démonstration · 1 min 45

**Sur la slide**
> **`APP-2026-08-25`** — le clic sur « Analyste crédit » depuis la page de résultat affichait :
> ```json
> {"detail":"Method Not Allowed"}
> ```
>
> **Diagnostic** : les liens de profil étaient relatifs — `href="?profil=analyste"`.
> Un lien relatif conserve le chemin **et émet un GET**. Sur `/`, `/transparence`, `/exploitation`
> — routes GET — il fonctionnait. Sur `/evaluer`, déclarée **POST** parce qu'elle répondait à un
> formulaire, il n'y avait aucun gestionnaire : **405**.
>
> **Correctif** : gestionnaire `GET /evaluer` partageant la même fonction de rendu ; liens
> **construits côté serveur**, conservant le cas évalué. Le gabarit ne fabrique plus d'URL.
>
> **Non-régression, vérifiée dans les deux sens** :
> correctif retiré → les 6 tests échouent, `GET /evaluer -> 405` journalisé. Correctif remis → verts.

**Script**
> Le premier que je détaille est celui qui cassait ma propre démonstration.
>
> Depuis la page de résultat, cliquer sur « Analyste crédit » affichait un JSON brut : « Method Not
> Allowed ». En plein milieu du parcours, sur l'étape censée être la plus convaincante — le même
> rapprochement, deux lectures.
>
> Le diagnostic est intéressant parce que la cause n'était pas où on la cherche. Les liens du
> bandeau étaient relatifs. Un lien relatif conserve le chemin courant et émet un GET. Sur mes trois
> pages en GET, il fonctionnait parfaitement. Sur la page de résultat, déclarée en POST parce
> qu'elle répondait à un formulaire, il n'y avait aucun gestionnaire.
>
> Le défaut n'était donc ni dans le modèle ni dans l'API : c'était une **hypothèse implicite du
> gabarit** — « toute page est atteignable en GET » — vraie pour trois pages sur quatre.
>
> Correctif en deux temps : un gestionnaire GET qui partage la même fonction de rendu, et des liens
> construits côté serveur. Six tests de non-régression, et je les ai vérifiés dans les deux sens :
> j'ai retiré le correctif pour confirmer qu'ils échouaient bien, avec le 405 dans le journal.

---

## Slide 5 bis — C21 : quand le poste ment · 1 min 15

**Sur la slide**
> **`CI-2026-08-25`** — six tests **verts en local**, **rouges en CI**. Et pas avec l'erreur attendue.
>
> ```
> assert 503 == 200          # pas 405 : ce n'était donc PAS le bug d'origine
> ```
>
> **Diagnostic** : les tests instanciaient l'application, qui joint l'API modèle en HTTP sur le
> port 8002. Cette API tourne en permanence sur le poste de développement — **jamais** sur un
> runner GitHub. Les tests portaient une **dépendance d'environnement implicite**.
>
> **Correctif** : une doublure remplace le transport HTTP. Le **vrai moteur** est conservé ; seul
> le saut réseau est retiré, car ces tests portent sur le routage, pas sur le transport.
>
> **Puis on vérifie que la doublure n'a pas neutralisé les tests** : correctif du 405 retiré → les
> six échouent à nouveau.

**Script**
> Un troisième, très court, parce que sa leçon est différente des deux autres.
>
> Six tests que je venais d'écrire passaient sur ma machine et échouaient en intégration continue.
> Le symptôme était instructif : ils échouaient en 503, pas en 405. Ce n'était donc pas le bug
> d'origine qui réapparaissait.
>
> Le 503 est le code que mon application renvoie quand elle ne joint pas l'API modèle. Or mes tests
> instanciaient l'application, qui appelle son amont en HTTP. Cette API tourne en permanence sur mon
> poste, et jamais sur un runner GitHub. Mes tests exigeaient donc silencieusement un service
> démarré — exactement le défaut qu'ils étaient censés empêcher chez les autres.
>
> J'ai remplacé le transport par une doublure, en conservant le vrai moteur. Et j'ai ensuite vérifié
> que cette doublure ne les avait pas rendus aveugles, en retirant le correctif du 405 : les six
> échouent bien.
>
> La règle que j'en tire : **un test qui réussit en local et échoue en CI ne signale pas un problème
> de CI. Il signale que le poste fournissait silencieusement quelque chose.**

---

## Slide 6 — C21 : quand l'outil de contrôle se trompe · 1 min 45

**Sur la slide**
> **`SEC-2026-08-25-bis`** — la porte de conformité affichait **CONFORME** alors que la chaîne
> d'entraînement était **cassée**.
>
> ```
> python -m concorde.model.entrainement
> ModuleNotFoundError: No module named 'alembic'      # code de sortie 1
> ```
>
> **Trois filets l'ont laissé passer** :
> 1. le test **neutralisait** la journalisation MLflow → le chemin cassé n'était jamais exercé
> 2. la porte **inspectait l'artefact** (présent, chargeable, contrat conforme) — les trois étaient
>    vrais : l'artefact valide était resté du passage précédent
> 3. la documentation **affirmait le contraire**
>
> **Correctif** : nouveau critère bloquant `qualite.chaine_entrainement`, qui **rejoue** la chaîne.
>
> > **Un artefact valide ne prouve que le passé.**

**Script**
> Le second est le plus intéressant, parce qu'il porte sur mon outil de contrôle lui-même.
>
> Pour corriger une vulnérabilité, j'avais changé de distribution MLflow. Le raisonnement était
> juste, mais la nouvelle distribution n'embarquait pas une dépendance du magasin de suivi. La
> chaîne d'entraînement ne fonctionnait plus.
>
> Ce qui rend cet incident instructif, c'est que **trois filets de sécurité l'ont laissé passer**.
> Le test neutralisait la journalisation, donc le chemin cassé n'était jamais exercé. La porte de
> conformité vérifiait que l'artefact existait, se chargeait et respectait son contrat — et les
> trois étaient vrais, parce qu'un artefact valide était resté sur le disque depuis le passage
> précédent. Et ma documentation affirmait explicitement le contraire de la réalité.
>
> La leçon tient en une phrase : **un artefact valide ne prouve que le passé.** Un contrôle qui
> inspecte un résultat ne prouve pas que le processus qui l'a produit fonctionne encore.
>
> J'ai donc ajouté un critère bloquant qui **rejoue** l'entraînement complet, dans un répertoire
> temporaire pour ne pas altérer l'artefact suivi. Vérifié dans les deux sens : dépendance retirée,
> la porte passe à non conforme et sort en code 1 ; dépendance remise, elle repasse au vert.

---

## Slide 7 — Le motif récurrent, et le bilan · 1 min

**Sur la slide**
> **Quatre incidents sur cinq avaient la même cause profonde :**
> **la documentation affirmait ce que le code ne faisait pas.**
>
> — le registre RGPD annonçait une minimisation que l'API ne respectait plus
> — le `.gitignore` affirmait un versionnement DVC inexistant
> — `docs/securite.md` affirmait un suivi MLflow qui ne fonctionnait pas
>
> **La correction, à chaque fois** : rendre l'affirmation vraie **et** la faire vérifier par un
> test ou un critère.
>
> **Ce que j'emporte de ce projet** : une preuve qui n'est pas exécutée n'est pas une preuve.

**Script**
> En reprenant mes cinq incidents, un motif est apparu, et c'est ce que j'emporte de ce projet.
>
> Quatre sur cinq avaient la même cause profonde : **la documentation affirmait ce que le code ne
> faisait pas.** Mon registre RGPD annonçait une minimisation que l'API ne respectait plus. Mon
> `.gitignore` affirmait un versionnement DVC qui n'existait pas. Ma documentation de sécurité
> affirmait un suivi MLflow qui était cassé.
>
> À chaque fois, la correction a consisté à faire deux choses, pas une : rendre l'affirmation
> vraie, **et** la faire vérifier automatiquement par un test ou un critère de conformité.
>
> C'est la raison pour laquelle mon registre RGPD est aujourd'hui protégé par un test, et pourquoi
> ma porte de conformité rejoue la chaîne au lieu d'inspecter son résultat.
>
> Une preuve qui n'est pas exécutée n'est pas une preuve. C'est ce que ce projet m'a appris, et
> c'est ce que je retiens au-delà de la certification.
>
> Je vous remercie, je suis à votre disposition pour vos questions.

---

## Aide-mémoire

**À montrer si on te le demande**
- la corrélation : `jq 'select(.request_id=="…")' monitoring/logs/*.jsonl`
- le tableau de bord : `http://127.0.0.1:8000/exploitation`
- un incident complet : `docs/incident.md`
- la porte qui refuse : retirer l'artefact → `python scripts/conformite.py` → **code 1**

**Questions probables**
- *Vos incidents sont-ils réels ou provoqués ?* → réels, tous datés, avec les exécutions CI publiques correspondantes. Je n'ai pas eu besoin d'en provoquer.
- *Comment savez-vous que vos tests de non-régression fonctionnent ?* → je les vérifie dans les deux sens : je retire le correctif et je confirme que le test échoue. Un test qui passe avant la correction ne prouve rien.
- *Que feriez-vous en production ?* → une alerte n'y déclencherait toujours aucune action automatique. Réentraîner automatiquement sur des données dérivées, c'est apprendre la dérive.
- *Et la conservation des journaux ?* → pseudonymisés à l'écriture, purgés après la soutenance ; c'est dans le registre RGPD.
