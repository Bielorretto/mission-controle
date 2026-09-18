import importlib.util
from pathlib import Path

_TOOLS_PATH = (
    Path(__file__).resolve().parent.parent / "mcp-servers" / "grist-mcp" / "tools.py"
)


def _load_grist_mcp_tools():
    spec = importlib.util.spec_from_file_location("grist_mcp_tools", _TOOLS_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


grist_mcp_tools = _load_grist_mcp_tools()


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        return self._payload


def _set_env(monkeypatch):
    monkeypatch.setenv("GRIST_BASE_URL", "http://localhost:8484")
    monkeypatch.setenv("GRIST_API_KEY", "test-key")
    monkeypatch.setenv("GRIST_DOC_ID", "test-doc-id")
    monkeypatch.setenv("GRIST_TABLE_ID", "Table1")


def test_get_records_returns_id_and_fields(monkeypatch):
    _set_env(monkeypatch)
    captured = {}

    def fake_get(url, headers=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        return FakeResponse(
            {
                "records": [
                    {"id": 1, "fields": {"Action": "A", "Statut": "À faire"}},
                    {"id": 2, "fields": {"Action": "B", "Statut": "Fait"}},
                ]
            }
        )

    monkeypatch.setattr(grist_mcp_tools.httpx, "get", fake_get)

    records = grist_mcp_tools.get_records()

    assert records == [
        {"id": 1, "Action": "A", "Statut": "À faire"},
        {"id": 2, "Action": "B", "Statut": "Fait"},
    ]
    assert captured["url"] == "http://localhost:8484/api/docs/test-doc-id/tables/Table1/records"
    assert captured["headers"]["Authorization"] == "Bearer test-key"


def test_get_records_uses_explicit_table_id(monkeypatch):
    _set_env(monkeypatch)
    captured = {}

    def fake_get(url, headers=None, timeout=None):
        captured["url"] = url
        return FakeResponse({"records": []})

    monkeypatch.setattr(grist_mcp_tools.httpx, "get", fake_get)

    grist_mcp_tools.get_records(table_id="OtherTable")

    assert captured["url"].endswith("/tables/OtherTable/records")


def test_get_records_empty_table(monkeypatch):
    _set_env(monkeypatch)
    monkeypatch.setattr(
        grist_mcp_tools.httpx, "get", lambda *a, **k: FakeResponse({"records": []})
    )

    assert grist_mcp_tools.get_records() == []


def test_list_tables_returns_table_and_columns(monkeypatch):
    _set_env(monkeypatch)
    calls = []

    def fake_get(url, headers=None, timeout=None):
        calls.append(url)
        if url.endswith("/tables"):
            return FakeResponse({"tables": [{"id": "Table1"}]})
        return FakeResponse(
            {"columns": [{"id": "Action"}, {"id": "Responsable"}]}
        )

    monkeypatch.setattr(grist_mcp_tools.httpx, "get", fake_get)

    result = grist_mcp_tools.list_tables()

    assert result == [{"table_id": "Table1", "columns": ["Action", "Responsable"]}]
    assert calls[0].endswith("/tables")
    assert calls[1].endswith("/tables/Table1/columns")


def test_get_records_raises_if_api_key_missing(monkeypatch):
    monkeypatch.delenv("GRIST_API_KEY", raising=False)
    monkeypatch.setenv("GRIST_DOC_ID", "test-doc-id")

    import pytest

    with pytest.raises(KeyError):
        grist_mcp_tools.get_records()
