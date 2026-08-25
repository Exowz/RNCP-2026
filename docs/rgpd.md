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

Limite : DVF, DPE et Géorisques sont des données publiques, mais leur
croisement peut augmenter le risque de ré-identification. Croiser une adresse
précise, un prix de vente et une étiquette énergétique désigne un logement, donc
potentiellement son occupant. Concorde ne publie donc ni fiche de bien ni
adresse complète dans l'API data.

## L'engagement de minimisation est testé, pas seulement écrit

L'adresse issue de la BAN reste présente dans la table interne
`data/processed/rapprochements.parquet`, où elle sert au rapprochement. Elle ne
franchit jamais la frontière de l'API.

Ce n'est pas une intention : c'est un test de non-régression.

```bash
pytest tests/api/test_api_data.py::test_aucune_adresse_detaillee_n_est_publiee_par_l_api_data
```

Il interroge les trois routes exposées et échoue si `adresse_ban` — ou une
adresse en clair — réapparaît dans une réponse, y compris par inadvertance en
élargissant un schéma de sortie. Un registre RGPD qu'aucun test ne protège finit
toujours par diverger du code qu'il décrit.

**Historique.** Le champ `adresse_ban` a été exposé le 25 août 2026 lors de
l'ajout des routes `/rapprochements`, puis retiré le jour même : il contredisait
l'engagement ci-dessus. La correction est accompagnée du test qui empêche sa
réapparition.
