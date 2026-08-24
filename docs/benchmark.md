# Benchmark des services IA existants — C7

Besoin residuel : reformuler en langage clair une reserve deja produite par les
regles et le moteur Concorde. Le service ne score pas les donnees, ne predit pas
de prix et ne recoit ni adresse ni identite.

| Service | Acces local/offline | Modele disponible | Cout/empreinte | Decision |
|---|---|---|---|---|
| **LM Studio + Gemma 4B** | API HTTP `127.0.0.1`, sans Internet apres chargement | `google/gemma-4-e4b`, 6,86 Go local | Inference sur poste ; pas de transfert de donnees ni GPU cloud | **Retenu** |
| Ollama | Local possible | Non installe ni modele local | Telechargement et duplication d'un poids inutiles ce soir | Ecarte |
| API LLM cloud | Depend du reseau et d'un tiers | Non necessaire | Cout variable, transfert de prompts, indisponible hors ligne | Ecarte |
| Modele scikit-learn interne | Deja present | Autoencodeur Concorde | Faible cout mais ce n'est pas un service IA tiers | Ecarte pour C7/C8 |

Choix : LM Studio est le seul service preexistant deja installe avec un modele
charge localement. La sobriete ne signifie pas qu'un LLM est gratuit : Concorde
ne l'appelle que pour le texte residuel, avec une limite de tokens, et prefere
les sorties structurees aux conversations longues.
