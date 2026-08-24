# Journal de decisions techniques

Une ligne par decision structurante : la date, la decision, l'alternative ecartee, la raison.
Ce journal est une preuve pour **C16** (conduite de projet) et alimente la section 5 des cinq
rapports (« Bilan, limites, decisions »).

Format : `AAAA-MM-JJ HH:MM | DECISION | ALTERNATIVE ECARTEE | RAISON`

---

## 2026-08-24 — Jour 1 : socle

**J1-01 — Un seul depot, deux livrables.**
Le socle technique est le projet de substitution n°21 « Secure MLOps » ; le domaine metier est un
moteur d'anomalie / coherence / confiance sur le croisement DVF+ x DPE x Georisques.
*Ecarte* : deux projets separes. *Raison* : trois jours seul. Un systeme etroit, complet et
demontrable vaut mieux que deux systemes troues. Les deux soutenances sont separees par des tags Git,
pas par des depots.

**J1-02 — Python 3.12, pas 3.13 ni 3.9.**
*Ecarte* : le Python 3.9 du systeme (trop ancien pour `pydantic-settings` et la syntaxe moderne des
types) ; Python 3.13 (roues PySpark 3.5 incompletes).
*Raison* : 3.12 est le plus grand denominateur commun entre PySpark 3.5, PyTorch 2.x, MLflow 3 et
Evidently 0.7. Contrainte inscrite dans `pyproject.toml` (`>=3.12,<3.13`) : elle est verifiee, pas
esperee.

**J1-03 — JDK 17 installe explicitement pour Spark.**
La machine ne portait qu'un JDK 26. Spark 3.5 ne supporte officiellement que Java 8/11/17.
*Raison* : la panne serait apparue au pire moment (C1 « systeme big data », C2 « Spark SQL »).
`JAVA_HOME` est fige dans `scripts/env.sh` et non laisse au hasard de la machine.

**J1-04 — Gestionnaire de paquets `uv`, verrou `uv.lock` versionne.**
*Ecarte* : `pip` + `requirements.txt` (resolution non deterministe), Poetry (plus lent).
*Raison* : reproductibilite exacte hors ligne. Le verrou fige les versions transitives ; la CI et la
machine de demonstration installent le meme graphe de dependances, a l'octet pres.

**J1-05 — Garde-fou hors ligne applicatif (`src/concorde/common/offline.py`).**
*Ecarte* : « couper le Wi-Fi le jour J ».
*Raison* : couper le reseau ne *prouve* rien et ne revele une dependance cachee qu'en soutenance.
Le verrou intercepte la couche socket et transforme toute sortie reseau non locale en erreur
explicite et localisee. C'est une preuve reproductible (`tests/test_offline_guard.py`), pas une
promesse.

**J1-06 — Journalisation JSON Lines avec pseudonymisation a l'ecriture.**
*Ecarte* : logs texte libre.
*Raison* : (1) exploitables par `jq` sans parsing fragile (C20) ; (2) un `request_id` traverse
app -> API -> modele, ce qui rend un incident rejouable (C21) ; (3) les champs personnels sont
haches **avant** ecriture disque, pour que le fichier de log ne devienne pas une base de donnees
personnelles clandestine (RGPD, C4/C20).

**J1-07 — Application en FastAPI + Jinja2 + CSS ecrit a la main.**
*Ecarte* : Streamlit (accessibilite non maitrisable, DOM genere) ; React/Vue (chaine de build npm,
risque de CDN, temps).
*Raison* : C14 et C17 exigent des preuves d'accessibilite WCAG/RGAA — reperes ARIA, ordre de
tabulation, contrastes, libelles de formulaire. Cela suppose de maitriser le HTML produit. Aucun
actif distant : tout est servi en local, ce qui satisfait la contrainte hors ligne.
