import pytest

from core.ollama_analyzer import OllamaMeetingAnalyzer


def test_ollama_analyzer_has_default_configuration() -> None:
    analyzer = OllamaMeetingAnalyzer()

    assert analyzer.base_url == "http://localhost:11434/v1"
    assert analyzer.model == "gemma4:12b-mlx"


def test_ollama_analyzer_rejects_empty_transcript() -> None:
    analyzer = OllamaMeetingAnalyzer()

    with pytest.raises(ValueError, match="Transcript cannot be empty"):
        analyzer.analyze("   ")


def test_ollama_analyzer_returns_meeting_analysis(monkeypatch) -> None:
    analyzer = OllamaMeetingAnalyzer()

    class FakeResponse:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict:
            return {
                "choices": [
                    {
                        "message": {
                            "content": """
                            {
                              "meeting_id": "meeting-001",
                              "title": "Réunion Mission Control",
                              "language": "fr",
                              "summary": "Présentation du projet Mission Control.",
                              "decisions": [
                                {
                                  "description": "Utiliser Mission Control pour le suivi des réunions."
                                }
                              ],
                              "actions": [
                                {
                                  "id": "action-001",
                                  "description": "Préparer la démonstration.",
                                  "assignee": "Celine",
                                  "due_date": null,
                                  "status": "todo"
                                }
                              ]
                            }
                            """
                        }
                    }
                ]
            }

    def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        "core.ollama_analyzer.httpx.post",
        fake_post,
    )

    result = analyzer.analyze(
        "Nous utiliserons Mission Control. Celine préparera la démonstration."
    )

    assert result.meeting_id == "meeting-001"
    assert result.title == "Réunion Mission Control"
    assert result.language == "fr"
    assert len(result.decisions) == 1
    assert len(result.actions) == 1
    assert result.actions[0].assignee == "Celine"
    assert result.actions[0].status == "todo"