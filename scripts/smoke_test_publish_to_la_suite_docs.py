"""Manual smoke test — NOT run automatically.

Publishes exactly ONE clearly-labelled test document to the locally running
La Suite Docs instance, using the real MissionControlOrchestrator ->
OllamaMeetingAnalyzer -> LaSuiteDocsPublisher flow. Never updates or deletes
any existing document; never prints credential values.

Requires these environment variables to be set (never hardcode them):
    LA_SUITE_DOCS_BASE_URL   (optional, defaults to http://localhost:18071/api/v1.0)
    LA_SUITE_DOCS_TOKEN
    LA_SUITE_DOCS_OWNER_SUB
    LA_SUITE_DOCS_OWNER_EMAIL

Usage:
    python3 scripts/smoke_test_publish_to_la_suite_docs.py [transcript_path]
"""

import dataclasses
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.integrations.la_suite_docs_publisher import LaSuiteDocsPublisher
from core.ollama_analyzer import OllamaMeetingAnalyzer
from core.orchestrator import MissionControlOrchestrator

DEFAULT_TRANSCRIPT_PATH = "samples/conseil_municipal_transcript.txt"


def main(argv: list[str]) -> int:
    transcript_path = argv[0] if argv else DEFAULT_TRANSCRIPT_PATH

    with open(transcript_path, encoding="utf-8") as f:
        transcript = f.read()

    publisher = LaSuiteDocsPublisher()
    tagged_title = {}

    def tagging_publisher(analysis):
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        tagged_analysis = dataclasses.replace(
            analysis,
            title=f"[Mission Control SMOKE TEST] {timestamp} - {analysis.title}",
        )
        tagged_title["value"] = tagged_analysis.title
        publisher(tagged_analysis)

    orchestrator = MissionControlOrchestrator(
        analyzer=OllamaMeetingAnalyzer(),
        publishers=[tagging_publisher],
    )

    orchestrator.run(transcript)

    print("Smoke test document published successfully.")
    print(f"Title:       {tagged_title['value']}")
    print(f"Document ID: {publisher.last_created_document_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
