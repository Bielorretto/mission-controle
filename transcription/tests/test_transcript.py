from pathlib import Path

import pytest

from mission_control.transcript import Transcript, load_transcript


DATA_DIR = Path(__file__).parent / "data"


def test_load_txt():
    transcript = load_transcript(DATA_DIR / "meeting.txt")

    assert isinstance(transcript, Transcript)
    assert transcript.format == "txt"
    assert "Celine" in transcript.content


def test_load_markdown():
    transcript = load_transcript(DATA_DIR / "meeting.md")

    assert isinstance(transcript, Transcript)
    assert transcript.format == "md"
    assert "# Project Alpha Meeting" in transcript.content


def test_preserve_french_accents():
    transcript = load_transcript(DATA_DIR / "french_accents.txt")

    assert "É" in transcript.content
    assert "é" in transcript.content
    assert "è" in transcript.content


def test_empty_transcript():
    with pytest.raises(ValueError, match="Transcript is empty"):
        load_transcript(DATA_DIR / "empty.txt")


def test_missing_file():
    with pytest.raises(FileNotFoundError, match="Transcript file not found"):
        load_transcript(DATA_DIR / "does-not-exist.txt")


def test_unsupported_extension():
    with pytest.raises(
        ValueError,
        match="Unsupported transcript format",
    ):
        load_transcript(DATA_DIR / "meeting.pdf")
