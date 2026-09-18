# suivi-mcp/tools.py
#
# Adapter only: wraps the already-validated MissionControlSuiviService so it
# can be called as an MCP tool. No analysis, formatting, Docs, Grist, or
# orchestration logic lives here — all of that stays in core/.

import sys
from pathlib import Path

from dotenv import load_dotenv

_SUIVI_MCP_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SUIVI_MCP_DIR.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

load_dotenv(_SUIVI_MCP_DIR / ".env")

from core.integrations.grist_publisher import GristPublisher
from core.integrations.la_suite_docs_publisher import LaSuiteDocsPublisher
from core.mission_control_service import MissionControlSuiviService, format_confirmation
from core.ollama_analyzer import OllamaMeetingAnalyzer


def organise_le_suivi(transcript: str) -> dict:
    service = MissionControlSuiviService(
        analyzer=OllamaMeetingAnalyzer(),
        docs_publisher=LaSuiteDocsPublisher(),
        grist_publisher=GristPublisher(),
    )

    result = service.organise_le_suivi(transcript)

    errors = {}
    if result.docs_error:
        errors["docs"] = result.docs_error
    if result.grist_error:
        errors["grist"] = result.grist_error

    return {
        "confirmation": format_confirmation(result),
        "success": result.success,
        "docs_document_id": result.docs_document_id,
        "grist_record_ids": result.grist_record_ids,
        "errors": errors,
    }
