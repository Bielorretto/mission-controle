import pytest

from tools import TranscriptSourceError, get_latest_meeting_transcript


def _write_transcript(tmp_path, name, content):
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def test_returns_fixture_transcript_with_expected_shape(tmp_path, monkeypatch):
    path = _write_transcript(tmp_path, "conseil_municipal.txt", "Bonjour tout le monde.")
    monkeypatch.delenv("MEET_SOURCE", raising=False)
    monkeypatch.setenv("MEET_TRANSCRIPT_FIXTURE_PATH", str(path))

    result = get_latest_meeting_transcript()

    assert result == {
        "meeting_id": "fixture-conseil_municipal",
        "title": "conseil municipal",
        "started_at": None,
        "ended_at": None,
        "participants": [],
        "transcript": "Bonjour tout le monde.",
        "source": "fixture",
    }


def test_defaults_to_fixture_source_when_meet_source_unset(tmp_path, monkeypatch):
    path = _write_transcript(tmp_path, "reunion.md", "# Réunion\nContenu.")
    monkeypatch.delenv("MEET_SOURCE", raising=False)
    monkeypatch.setenv("MEET_TRANSCRIPT_FIXTURE_PATH", str(path))

    result = get_latest_meeting_transcript()

    assert result["source"] == "fixture"
    assert result["transcript"] == "# Réunion\nContenu."


def test_accepts_markdown_fixture(tmp_path, monkeypatch):
    path = _write_transcript(tmp_path, "notes.md", "- point A\n- point B")
    monkeypatch.setenv("MEET_SOURCE", "fixture")
    monkeypatch.setenv("MEET_TRANSCRIPT_FIXTURE_PATH", str(path))

    result = get_latest_meeting_transcript()

    assert result["transcript"] == "- point A\n- point B"


def test_raises_clear_error_when_fixture_file_missing(tmp_path, monkeypatch):
    missing_path = tmp_path / "does_not_exist.txt"
    monkeypatch.setenv("MEET_SOURCE", "fixture")
    monkeypatch.setenv("MEET_TRANSCRIPT_FIXTURE_PATH", str(missing_path))

    with pytest.raises(TranscriptSourceError, match="not found"):
        get_latest_meeting_transcript()


def test_raises_clear_error_for_unsupported_extension(tmp_path, monkeypatch):
    path = _write_transcript(tmp_path, "transcript.json", '{"foo": "bar"}')
    monkeypatch.setenv("MEET_SOURCE", "fixture")
    monkeypatch.setenv("MEET_TRANSCRIPT_FIXTURE_PATH", str(path))

    with pytest.raises(TranscriptSourceError, match="Unsupported transcript file type"):
        get_latest_meeting_transcript()


def test_raises_clear_error_for_empty_fixture(tmp_path, monkeypatch):
    path = _write_transcript(tmp_path, "empty.txt", "   \n  ")
    monkeypatch.setenv("MEET_SOURCE", "fixture")
    monkeypatch.setenv("MEET_TRANSCRIPT_FIXTURE_PATH", str(path))

    with pytest.raises(TranscriptSourceError, match="is empty"):
        get_latest_meeting_transcript()


def test_does_not_silently_fall_back_when_meet_source_is_not_fixture(monkeypatch):
    monkeypatch.setenv("MEET_SOURCE", "visio")

    with pytest.raises(TranscriptSourceError, match="not implemented"):
        get_latest_meeting_transcript()


def test_uses_default_repo_fixture_path_when_env_var_unset(monkeypatch):
    monkeypatch.delenv("MEET_SOURCE", raising=False)
    monkeypatch.delenv("MEET_TRANSCRIPT_FIXTURE_PATH", raising=False)

    result = get_latest_meeting_transcript()

    assert result["source"] == "fixture"
    assert result["meeting_id"] == "fixture-conseil_municipal_transcript"
    assert "conseil municipal" in result["title"].lower()
    assert result["transcript"]
