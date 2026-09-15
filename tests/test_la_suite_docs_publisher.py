import pytest

from core.integrations.la_suite_docs_publisher import LaSuiteDocsPublisher
from core.integrations.markdown_formatter import format_meeting_analysis_as_markdown
from core.models import ActionItem, Decision, MeetingAnalysis


def _make_analysis(**overrides) -> MeetingAnalysis:
    defaults = dict(
        meeting_id="meeting-001",
        title="Réunion Test",
        language="fr",
        summary="Résumé de test.",
        decisions=[Decision(description="Décision A")],
        actions=[
            ActionItem(
                id="action-1",
                description="Faire le point",
                assignee="Alice",
                due_date="2026-01-01",
            )
        ],
    )
    defaults.update(overrides)
    return MeetingAnalysis(**defaults)


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        return self._payload


def _make_fake_post(captured: dict):
    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        return FakeResponse({"id": "doc-123"})

    return fake_post


def _make_publisher(**overrides) -> LaSuiteDocsPublisher:
    defaults = dict(
        base_url="http://localhost:18071/api/v1.0",
        token="test-token",
        owner_sub="owner-sub",
        owner_email="owner@example.com",
    )
    defaults.update(overrides)
    return LaSuiteDocsPublisher(**defaults)


def test_markdown_includes_title_and_summary() -> None:
    md = format_meeting_analysis_as_markdown(_make_analysis())

    assert "# Réunion Test" in md
    assert "## Résumé" in md
    assert "Résumé de test." in md


def test_markdown_formats_decisions() -> None:
    analysis = _make_analysis(
        decisions=[
            Decision(description="Décision A"),
            Decision(description="Décision B"),
        ]
    )

    md = format_meeting_analysis_as_markdown(analysis)

    assert "- Décision A" in md
    assert "- Décision B" in md


def test_markdown_formats_actions() -> None:
    md = format_meeting_analysis_as_markdown(_make_analysis())

    assert (
        "- [ ] Faire le point — Responsable: Alice — Échéance: 2026-01-01" in md
    )


def test_markdown_handles_missing_assignee() -> None:
    analysis = _make_analysis(
        actions=[
            ActionItem(
                id="action-1",
                description="Tâche sans responsable",
                assignee=None,
                due_date="2026-01-01",
            )
        ]
    )

    md = format_meeting_analysis_as_markdown(analysis)

    assert "Responsable: Non assigné" in md


def test_markdown_handles_missing_due_date() -> None:
    analysis = _make_analysis(
        actions=[
            ActionItem(
                id="action-1",
                description="Tâche sans échéance",
                assignee="Bob",
                due_date=None,
            )
        ]
    )

    md = format_meeting_analysis_as_markdown(analysis)

    assert "Échéance: Non définie" in md


def test_publisher_posts_to_create_for_owner_url(monkeypatch) -> None:
    captured: dict = {}
    monkeypatch.setattr(
        "core.integrations.la_suite_docs_client.httpx.post",
        _make_fake_post(captured),
    )

    publisher = _make_publisher()
    result = publisher(_make_analysis())

    assert result is None
    assert captured["url"] == "http://localhost:18071/api/v1.0/documents/create-for-owner/"


def test_publisher_sends_expected_payload(monkeypatch) -> None:
    captured: dict = {}
    monkeypatch.setattr(
        "core.integrations.la_suite_docs_client.httpx.post",
        _make_fake_post(captured),
    )

    publisher = _make_publisher()
    analysis = _make_analysis()
    publisher(analysis)

    payload = captured["json"]
    assert payload["title"] == analysis.title
    assert payload["sub"] == "owner-sub"
    assert payload["email"] == "owner@example.com"
    assert "## Résumé" in payload["content"]
    assert "## Décisions" in payload["content"]
    assert "## Actions" in payload["content"]


def test_publisher_sends_bearer_authorization_header(monkeypatch) -> None:
    captured: dict = {}
    monkeypatch.setattr(
        "core.integrations.la_suite_docs_client.httpx.post",
        _make_fake_post(captured),
    )

    publisher = _make_publisher(token="secret-token")
    publisher(_make_analysis())

    assert captured["headers"]["Authorization"] == "Bearer secret-token"


def test_publisher_stores_created_document_id(monkeypatch) -> None:
    captured: dict = {}
    monkeypatch.setattr(
        "core.integrations.la_suite_docs_client.httpx.post",
        _make_fake_post(captured),
    )

    publisher = _make_publisher()
    publisher(_make_analysis())

    assert publisher.last_created_document_id == "doc-123"


def test_publisher_reads_configuration_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("LA_SUITE_DOCS_BASE_URL", "http://localhost:18071/api/v1.0")
    monkeypatch.setenv("LA_SUITE_DOCS_TOKEN", "env-token")
    monkeypatch.setenv("LA_SUITE_DOCS_OWNER_SUB", "env-sub")
    monkeypatch.setenv("LA_SUITE_DOCS_OWNER_EMAIL", "env-owner@example.com")

    publisher = LaSuiteDocsPublisher()

    assert publisher.base_url == "http://localhost:18071/api/v1.0"
    assert publisher.token == "env-token"
    assert publisher.owner_sub == "env-sub"
    assert publisher.owner_email == "env-owner@example.com"


def test_publisher_raises_if_token_missing_from_environment(monkeypatch) -> None:
    monkeypatch.delenv("LA_SUITE_DOCS_TOKEN", raising=False)
    monkeypatch.setenv("LA_SUITE_DOCS_OWNER_SUB", "env-sub")
    monkeypatch.setenv("LA_SUITE_DOCS_OWNER_EMAIL", "env-owner@example.com")

    with pytest.raises(KeyError):
        LaSuiteDocsPublisher()
