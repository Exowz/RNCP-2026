"""Contrat de securite de la reformulation locale, sans LM Studio reel."""

from __future__ import annotations

from typing import Any

from concorde.service import lm_studio
from concorde.service.lm_studio import ClientLMStudio


def test_reformuler_accepte_seulement_une_phrase_finale_sans_raisonnement(monkeypatch) -> None:
    """Un raisonnement cache ne devient jamais un texte adresse a l'utilisateur."""
    appels: list[dict[str, Any]] = []

    class Reponse:
        status_code = 200

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, Any]:
            return {
                "choices": [{"message": {"content": "Une verification reste necessaire avant utilisation."}, "finish_reason": "stop"}],
                "usage": {"completion_tokens_details": {"reasoning_tokens": 0}},
            }

    class ClientHTTP:
        def __init__(self, timeout: float) -> None:
            assert timeout == 3.0

        def __enter__(self) -> ClientHTTP:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def post(self, url: str, json: dict[str, Any]) -> Reponse:
            assert url == "http://127.0.0.1:1234/v1/chat/completions"
            appels.append(json)
            return Reponse()

    monkeypatch.setattr(lm_studio.httpx, "Client", ClientHTTP)
    monkeypatch.setattr(lm_studio.metriques, "deverser", lambda _chemin: None)

    texte = ClientLMStudio(
        url_base="http://127.0.0.1:1234/v1", modele="google/gemma-4-e4b"
    ).reformuler_verdict(
        {
            "statut": "evalue",
            "niveau_anomalie": "a_verifier",
            "score_coherence": 0.6,
            "motifs": [{"gravite": "majeur", "message": "Surfaces contradictoires."}],
            "confiance": {"niveau": "moyen", "reserves": []},
            "explication": "Une verification est necessaire.",
        }
    )

    assert texte == "Une verification reste necessaire avant utilisation."
    assert appels[0]["temperature"] == 0
    assert appels[0]["max_tokens"] == 90
    assert "Repond UNIQUEMENT" in appels[0]["messages"][0]["content"]
    assert "score_coherence" not in appels[0]["messages"][1]["content"]
