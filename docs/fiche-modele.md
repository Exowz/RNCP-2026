# Fiche du modele — Concorde, moteur de confiance

Document genere par `python -m concorde.model.entrainement`. Ne pas editer a la main.

## Identite

| Champ | Valeur |
|---|---|
| Version | `0.1.0` |
| Entraine le | 2026-08-24T19:10:18.399502+00:00 |
| Commit Git | `02b6229` |
| Graine aleatoire | `20260824` |
| Empreinte du jeu d'entrainement | `a987ffdce586ad1f9961e4123bf468fd...` |
| Lignes d'entrainement / validation | 499 / 109 |

## Objet

Le modele **ne predit ni prix ni valeur**. Il qualifie la fiabilite d'un rapprochement entre une mutation DVF+ et un DPE ADEME, sur trois axes independants : coherence (regles metier explicites), anomalie (auto-encodeur non supervise), confiance (completude et precision de l'information disponible).

## Variables soumises au detecteur

- `ecart_surface_rel`
- `ecart_temporel_annees`
- `dpe_posterieur_mutation`
- `desaccord_type_local`
- `log_prix_m2`
- `ecart_prix_m2_commune`
- `anciennete_bati`
- `conso_kwh_m2_an`

## Metriques (jeu de test)

| Metrique | Valeur | Lecture |
|---|---:|---|
| `perte_validation` | 0.227485 | Erreur quadratique de reconstruction sur la validation. |
| `epoques_effectuees` | 220 | Arret anticipe sur la perte de validation. |
| `nb_test` | 108 | Taille du jeu de test. |
| `taux_signalement_atypique` | 0.1204 | Part du jeu de test signalee comme atypique. |
| `auc_autoencodeur` | 0.9095 | **Informatif.** Pouvoir de tri de l'auto-encodeur seul, qui n'a vu ni les regles ni les etiquettes. |
| `average_precision_autoencodeur` | 0.8427 | **Informatif.** Precision moyenne, robuste au desequilibre des classes. |
| `taux_base_anomalies` | 0.2407 | Proportion d'anomalies dans le jeu de test (reference). |
| `regles_precision_circulaire` | 0.8824 | **Circulaire.** Les regles visent les memes familles de contradictions que celles plantees. |
| `regles_rappel_circulaire` | 0.5769 | **Circulaire.** A ne pas presenter comme une performance. |
| `regles_f1_circulaire` | 0.6977 | **Circulaire.** |
| `systeme_precision` | 0.8889 | Systeme complet tel qu'il alerte (regles majeures OU score >= percentile 95). |
| `systeme_rappel` | 0.6154 | Systeme complet. |
| `systeme_f1` | 0.7273 | Systeme complet. |

## Limites assumees

- Le detecteur est non supervise : aucune etiquette « rapprochement faux » n'existe dans les donnees publiques.
- Les regles de coherence et les anomalies du jeu de demonstration relevent des memes familles de contradictions : le rappel des regles est circulaire et n'est pas une mesure de performance.
- La base DPE de l'ADEME n'est pas representative du parc francais ; aucune generalisation a l'echelle nationale n'est possible.
- Le rapprochement s'appuie sur la parcelle cadastrale : il est ambigu en copropriete, ce que le systeme signale sans le resoudre.
- Le modele ne predit ni prix ni valeur : il qualifie la fiabilite d'un rapprochement.

## Reproduction

```bash
python scripts/make_sample_fixture.py
python -m concorde.collect
python -m concorde.clean
python -m concorde.model.entrainement
```

Artefact produit : `models/concorde_moteur.pt` (graine `20260824`, resultat deterministe).