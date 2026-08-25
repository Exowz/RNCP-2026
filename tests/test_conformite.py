"""Contrat de la porte de conformité du projet de substitution n°21."""

from scripts.conformite import Critere, Verdict, code_retour, rendre_markdown


def _critere(verdict: Verdict, bloquant: bool = True) -> Critere:
    return Critere(
        identifiant="qualite.tests",
        axe="qualite",
        libelle="Tests",
        seuil="0 echec",
        valeur_mesuree="0 echec",
        verdict=verdict,
        justification_seuil="Un deploiement ne doit pas embarquer une regression connue.",
        bloquant=bloquant,
    )


def test_porte_refuse_un_critere_bloquant_non_conforme() -> None:
    """Detecte une porte verte malgre une non-conformite de deploiement."""
    assert code_retour([_critere(Verdict.NON_CONFORME)]) == 1


def test_porte_ne_fait_pas_passer_un_critere_non_evalue_pour_conforme() -> None:
    """Detecte un mode hors ligne qui masquerait l'absence de mesure de securite."""
    rapport = rendre_markdown([_critere(Verdict.NON_EVALUE)], "2026-08-26T12:00:00+00:00")

    assert code_retour([_critere(Verdict.NON_EVALUE)]) == 0
    assert "non évalué" in rapport
    assert "conforme" not in rapport.split("non évalué", maxsplit=1)[0]
