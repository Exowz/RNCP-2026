# Veille technique et reglementaire — C6

Date de revue : 24 aout 2026. Responsable : candidat seul ; il n'y a pas de
collectif a simuler. La veille est partagee dans ce depot par commits et dans
le journal de decisions. Limite assumee : pas d'animation d'equipe possible.

| Source qualifiee | Point surveille | Decision Concorde |
|---|---|---|
| [ADEME — Observatoire DPE-Audit](https://observatoire-dpe-audit.ademe.fr/statistiques/outil?trk=public_post_comment-text) | La base DPE ne couvre pas tout le parc et n'en est pas representative. | Ne jamais presenter un DPE brut comme une verite nationale ; afficher reserves et confiance. |
| [CNIL — recommandations IA et RGPD](https://www.cnil.fr/fr/developpement-des-systemes-dia-les-recommandations-de-la-cnil-pour-respecter-le-rgpd) | Finalite, information, limitation et possibilite d'arreter un systeme IA. | LLM limite a une fonction explicative locale, sans decision ni enrichissement de donnees. |
| [CNIL — securite des donnees](https://www.cnil.fr/fr/guide-de-la-securite-des-donnees-personnelles-nouvelle-edition-2024) | Le guide inclut des fiches IA et API ; securite proportionnee au risque. | Cles API, validation, logs pseudonymises, CI et incident documente. |
| [CNIL — scraping et IA](https://cnil.fr/fr/les-fiches-pratiques-ia) | Le moissonnage impose des mesures pour les droits des personnes. | Scraping cible, cache local, pas de donnees personnelles dans la sortie. |

Rythme : revue quotidienne jusqu'a la soutenance ; tout changement reglementaire
ou technique est consigne dans `docs/journal-decisions.md` avec impact sur les
preuves. La veille ne transforme pas une source en exigence automatique : elle
declenche une decision tracee et proportionnee.
