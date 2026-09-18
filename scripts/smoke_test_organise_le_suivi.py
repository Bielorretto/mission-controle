"""Manual smoke test — NOT run automatically.

Runs the real "organise le suivi" flow end to end against a fictional Buzz
conversation: real local Gemma analysis, a real La Suite Docs document, and
real Grist rows. Does NOT publish anything back into a real Buzz channel.

Requires these environment variables to be set (never hardcode them):
    LA_SUITE_DOCS_TOKEN, LA_SUITE_DOCS_OWNER_SUB, LA_SUITE_DOCS_OWNER_EMAIL
    GRIST_API_KEY, GRIST_DOC_ID

Usage:
    python3 scripts/smoke_test_organise_le_suivi.py
"""

import dataclasses
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.integrations.grist_publisher import GristPublisher
from core.integrations.la_suite_docs_publisher import LaSuiteDocsPublisher
from core.mission_control_service import MissionControlSuiviService, format_confirmation
from core.ollama_analyzer import OllamaMeetingAnalyzer

DEMO_TRANSCRIPT = """\
Sarah: Le pilote du nouveau service a été validé dans les trois départements.
Karim: Je transmets la liste des agents concernés mercredi.
Sarah: Parfait. Je pourrai préparer la configuration technique vendredi une \
fois la liste reçue.
Nadia: On garde le prochain point de suivi lundi à 14h.
"""


def main(argv: list[str]) -> int:
    service = MissionControlSuiviService(
        analyzer=OllamaMeetingAnalyzer(),
        docs_publisher=LaSuiteDocsPublisher(),
        grist_publisher=GristPublisher(),
    )

    result = service.organise_le_suivi(DEMO_TRANSCRIPT)

    print(f"Analysis: {dataclasses.asdict(result.analysis)}")
    print()
    print(format_confirmation(result))

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
