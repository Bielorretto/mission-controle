# meet-mcp/tools.py
#
# Only a fixture-backed transcript source is implemented today. There is no
# confirmed, reachable Meet/Visio API or documented transcript endpoint for
# this project, so no real integration is implemented and no endpoint is
# guessed at.
#
# The MEET_SOURCE boundary below exists so a real Meet/Visio implementation
# can later be plugged in without changing the MCP tool contract (the return
# shape of get_latest_meeting_transcript). If MEET_SOURCE is ever set to
# something other than "fixture", this raises a clear error instead of
# silently using the fixture.

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

SUPPORTED_TRANSCRIPT_EXTENSIONS = {".txt", ".md"}

_MEET_MCP_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _MEET_MCP_DIR.parent.parent
DEFAULT_FIXTURE_PATH = str(_REPO_ROOT / "samples" / "conseil_municipal_transcript.txt")


class TranscriptSourceError(RuntimeError):
    """Raised when a meeting transcript cannot be retrieved."""


def _read_fixture_transcript(path_str: str) -> str:
    path = Path(path_str)

    if not path.exists():
        raise TranscriptSourceError(
            f"Fixture transcript not found at '{path}'. "
            "Set MEET_TRANSCRIPT_FIXTURE_PATH to a valid .txt or .md file."
        )

    if path.suffix.lower() not in SUPPORTED_TRANSCRIPT_EXTENSIONS:
        raise TranscriptSourceError(
            f"Unsupported transcript file type '{path.suffix}' for '{path}'. "
            f"Supported types: {sorted(SUPPORTED_TRANSCRIPT_EXTENSIONS)}."
        )

    text = path.read_text(encoding="utf-8").strip()

    if not text:
        raise TranscriptSourceError(f"Fixture transcript at '{path}' is empty.")

    return text


def _get_latest_meeting_transcript_fixture() -> dict:
    fixture_path = os.environ.get("MEET_TRANSCRIPT_FIXTURE_PATH", DEFAULT_FIXTURE_PATH)
    transcript = _read_fixture_transcript(fixture_path)

    # These fields are intentionally left empty/None rather than parsed or
    # guessed from the fixture file: a plain .txt/.md transcript has no
    # reliable structured metadata, and we never pretend fixture data came
    # from a real Meet/Visio service.
    return {
        "meeting_id": f"fixture-{Path(fixture_path).stem}",
        "title": Path(fixture_path).stem.replace("_", " ").replace("-", " ").strip(),
        "started_at": None,
        "ended_at": None,
        "participants": [],
        "transcript": transcript,
        "source": "fixture",
    }


def get_latest_meeting_transcript() -> dict:
    """Return the latest meeting transcript in a stable, tool-contract shape.

    MEET_SOURCE selects the backing implementation:
    - "fixture" (default): read a local .txt/.md transcript file for demo use.
    - anything else: no real Meet/Visio integration exists yet, so this
      raises TranscriptSourceError instead of silently falling back to the
      fixture.
    """
    source = os.environ.get("MEET_SOURCE", "fixture")

    if source == "fixture":
        return _get_latest_meeting_transcript_fixture()

    raise TranscriptSourceError(
        f"MEET_SOURCE='{source}' is not implemented. Only 'fixture' is "
        "currently supported because no confirmed Meet/Visio API is "
        "available. Set MEET_SOURCE=fixture (or unset it) to use the demo "
        "transcript."
    )


if __name__ == "__main__":
    import json

    print(json.dumps(get_latest_meeting_transcript(), ensure_ascii=False, indent=2))
