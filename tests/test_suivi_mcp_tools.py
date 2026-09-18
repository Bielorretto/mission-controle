import importlib.util
from pathlib import Path

import pytest

_TOOLS_PATH = (
    Path(__file__).resolve().parent.parent / "mcp-servers" / "suivi-mcp" / "tools.py"
)


def _load_suivi_mcp_tools():
    spec = importlib.util.spec_from_file_location("suivi_mcp_tools", _TOOLS_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


suivi_mcp_tools = _load_suivi_mcp_tools()


class FakeAnalyzer:
    def __init__(self, *args, **kwargs) -> None:
        pass


class FakeDocsPublisher:
    last_created_document_id = "doc-777"
    received_transcript = None

    def __init__(self, *args, **kwargs) -> None:
        pass

    def __call__(self, analysis) -> None:
        FakeDocsPublisher.received_analysis = analysis


class FakeGristPublisher:
    last_created_record_ids = [10, 11]
    received_actions = None

    def __init__(self, *args, **kwargs) -> None:
        pass

    def __call__(self, actions) -> None:
        FakeGristPublisher.received_actions = actions


class FakeFailingGristPublisher(FakeGristPublisher):
    last_created_record_ids = []

    def __call__(self, actions) -> None:
        raise RuntimeError("grist unreachable")


def _make_fake_analysis(transcript: str):
    from core.models import ActionItem, Decision, MeetingAnalysis

    assert transcript == "CAPTURED"

    return MeetingAnalysis(
        meeting_id="meeting-001",
        title="Suivi",
        language="fr",
        summary="Résumé.",
        decisions=[Decision(description="Décision A")],
        actions=[
            ActionItem(
                id="action-1",
                description="Action A",
                assignee="Karim",
                due_date="Mercredi",
                status="todo",
                dependency="Bloque la suite",
            )
        ],
    )


@pytest.fixture
def patched_service(monkeypatch):
    captured_transcript = {}

    class CapturingAnalyzer(FakeAnalyzer):
        def analyze(self, transcript: str):
            captured_transcript["value"] = transcript
            return _make_fake_analysis("CAPTURED") if transcript == "CAPTURED" else None

    monkeypatch.setattr(suivi_mcp_tools, "OllamaMeetingAnalyzer", CapturingAnalyzer)
    monkeypatch.setattr(suivi_mcp_tools, "LaSuiteDocsPublisher", FakeDocsPublisher)
    monkeypatch.setattr(suivi_mcp_tools, "GristPublisher", FakeGristPublisher)

    return captured_transcript


def test_transcript_reaches_service_unchanged(patched_service):
    suivi_mcp_tools.organise_le_suivi("CAPTURED")

    assert patched_service["value"] == "CAPTURED"


def test_returned_confirmation_is_preserved(patched_service):
    result = suivi_mcp_tools.organise_le_suivi("CAPTURED")

    assert "Suivi préparé." in result["confirmation"]
    assert "Bloque la suite" in result["confirmation"]


def test_returns_docs_document_id(patched_service):
    result = suivi_mcp_tools.organise_le_suivi("CAPTURED")

    assert result["docs_document_id"] == "doc-777"


def test_returns_grist_record_ids(patched_service):
    result = suivi_mcp_tools.organise_le_suivi("CAPTURED")

    assert result["grist_record_ids"] == [10, 11]


def test_success_true_and_no_errors_on_happy_path(patched_service):
    result = suivi_mcp_tools.organise_le_suivi("CAPTURED")

    assert result["success"] is True
    assert result["errors"] == {}


def test_grist_failure_is_represented_as_error(monkeypatch):
    captured_transcript = {}

    class CapturingAnalyzer(FakeAnalyzer):
        def analyze(self, transcript: str):
            captured_transcript["value"] = transcript
            return _make_fake_analysis("CAPTURED")

    monkeypatch.setattr(suivi_mcp_tools, "OllamaMeetingAnalyzer", CapturingAnalyzer)
    monkeypatch.setattr(suivi_mcp_tools, "LaSuiteDocsPublisher", FakeDocsPublisher)
    monkeypatch.setattr(suivi_mcp_tools, "GristPublisher", FakeFailingGristPublisher)

    result = suivi_mcp_tools.organise_le_suivi("CAPTURED")

    assert result["success"] is False
    assert result["errors"] == {"grist": "grist unreachable"}
    assert result["docs_document_id"] == "doc-777"


def test_adapter_does_not_publish_to_buzz(monkeypatch, patched_service):
    import subprocess

    calls = []
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: calls.append((a, k)))
    monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: calls.append((a, k)))
    monkeypatch.setattr("os.system", lambda *a, **k: calls.append((a, k)))

    suivi_mcp_tools.organise_le_suivi("CAPTURED")

    assert calls == []
