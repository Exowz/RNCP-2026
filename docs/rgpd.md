# Registre RGPD minimal — C4 et C20

| Element | Decision |
|---|---|
| Finalite | Evaluer la coherence de donnees immobilieres publiques, jamais noter une personne ni tarifer un risque. |
| Responsable | Candidat RNCP, demonstration pedagogique locale. |
| Donnees | Codes INSEE, valeurs de transaction agregees, DPE, niveaux d'aleas. Aucun nom, email, telephone ou proprietaire. |
| Base legale | Mission pedagogique et interet legitime de qualite des donnees publiques ; pas de decision automatisee sur une personne. |
| Minimisation | L'API data expose une synthese communale ; les adresses detaillees ne sont ni en base PostgreSQL ni dans les logs. |
| Conservation | Fixtures jusqu'a la fin de l'evaluation ; logs techniques purges apres soutenance. |
| Securite | Cle API par role, validation Pydantic, en-tetes OWASP, secrets hors Git, pseudonymisation des IP dans les journaux. |
| Droits | Pas de sujet de donnees dans la base de demonstration ; toute demande est orientee vers la source publique d'origine. |

Limite : DVF, DPE et Géorisques sont des donnees publiques, mais leur
croisement peut augmenter le risque de re-identification. Concorde ne publie
donc pas de fiche de bien ni d'adresse complete dans l'API data.
