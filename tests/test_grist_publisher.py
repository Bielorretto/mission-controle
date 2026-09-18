import pytest

from core.integrations.grist_publisher import GristPublisher


def _make_action(**overrides) -> dict:
    defaults = dict(
        Action="Transmettre la liste des agents concernés",
        Responsable="Karim",
        Echeance="Mercredi",
        Statut="À faire",
        Dependance="Bloque la préparation technique prévue vendredi",
        Source="Réunion de déploiement",
    )
    defaults.update(overrides)
    return defaults


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
        return FakeResponse({"records": [{"id": 1}]})

    return fake_post


def _make_publisher(**overrides) -> GristPublisher:
    defaults = dict(
        base_url="http://localhost:8484",
        api_key="test-api-key",
        doc_id="aG4Xn76KHQyYt8nzYKS38s",
        table_id="Table1",
    )
    defaults.update(overrides)
    return GristPublisher(**defaults)


def test_publisher_posts_to_records_url(monkeypatch) -> None:
    captured: dict = {}
    monkeypatch.setattr(
        "core.integrations.grist_client.httpx.post",
        _make_fake_post(captured),
    )

    publisher = _make_publisher()
    result = publisher([_make_action()])

    assert result is None
    assert (
        captured["url"]
        == "http://localhost:8484/api/docs/aG4Xn76KHQyYt8nzYKS38s/tables/Table1/records"
    )


def test_publisher_sends_expected_payload(monkeypatch) -> None:
    captured: dict = {}
    monkeypatch.setattr(
        "core.integrations.grist_client.httpx.post",
        _make_fake_post(captured),
    )

    publisher = _make_publisher()
    publisher([_make_action()])

    payload = captured["json"]
    assert payload == {
        "records": [
            {
                "fields": {
                    "Action": "Transmettre la liste des agents concernés",
                    "Responsable": "Karim",
                    "Echeance": "Mercredi",
                    "Statut": "À faire",
                    "Dependance": "Bloque la préparation technique prévue vendredi",
                    "Source": "Réunion de déploiement",
                }
            }
        ]
    }


def test_publisher_sends_bearer_authorization_header(monkeypatch) -> None:
    captured: dict = {}
    monkeypatch.setattr(
        "core.integrations.grist_client.httpx.post",
        _make_fake_post(captured),
    )

    publisher = _make_publisher(api_key="secret-key")
    publisher([_make_action()])

    assert captured["headers"]["Authorization"] == "Bearer secret-key"


def test_publisher_supports_multiple_actions(monkeypatch) -> None:
    captured: dict = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["json"] = json
        return FakeResponse({"records": [{"id": 1}, {"id": 2}]})

    monkeypatch.setattr("core.integrations.grist_client.httpx.post", fake_post)

    publisher = _make_publisher()
    publisher([_make_action(), _make_action(Action="Autre action")])

    assert len(captured["json"]["records"]) == 2


def test_publisher_stores_created_record_ids(monkeypatch) -> None:
    captured: dict = {}
    monkeypatch.setattr(
        "core.integrations.grist_client.httpx.post",
        _make_fake_post(captured),
    )

    publisher = _make_publisher()
    publisher([_make_action()])

    assert publisher.last_created_record_ids == [1]


def test_publisher_reads_configuration_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("GRIST_BASE_URL", "http://localhost:8484")
    monkeypatch.setenv("GRIST_API_KEY", "env-key")
    monkeypatch.setenv("GRIST_DOC_ID", "env-doc-id")
    monkeypatch.setenv("GRIST_TABLE_ID", "Table1")

    publisher = GristPublisher()

    assert publisher.base_url == "http://localhost:8484"
    assert publisher.api_key == "env-key"
    assert publisher.doc_id == "env-doc-id"
    assert publisher.table_id == "Table1"


def test_publisher_defaults_table_id_when_not_set(monkeypatch) -> None:
    monkeypatch.setenv("GRIST_API_KEY", "env-key")
    monkeypatch.setenv("GRIST_DOC_ID", "env-doc-id")
    monkeypatch.delenv("GRIST_TABLE_ID", raising=False)

    publisher = GristPublisher()

    assert publisher.table_id == "Table1"


def test_publisher_raises_if_api_key_missing_from_environment(monkeypatch) -> None:
    monkeypatch.delenv("GRIST_API_KEY", raising=False)
    monkeypatch.setenv("GRIST_DOC_ID", "env-doc-id")

    with pytest.raises(KeyError):
        GristPublisher()
