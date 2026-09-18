from dataclasses import dataclass, field

from core.analysis import MeetingAnalyzer
from core.models import ActionItem, MeetingAnalysis

DEFAULT_SOURCE = "Conversation Buzz"

STATUS_LABELS = {
    "todo": "À faire",
}


@dataclass
class SuiviResult:
    analysis: MeetingAnalysis
    docs_document_id: str | None = None
    docs_error: str | None = None
    grist_record_ids: list[int] = field(default_factory=list)
    grist_error: str | None = None

    @property
    def success(self) -> bool:
        return self.docs_error is None and self.grist_error is None

    @property
    def blockers(self) -> list[str]:
        return [action.dependency for action in self.analysis.actions if action.dependency]


def action_to_grist_fields(action: ActionItem) -> dict:
    return {
        "Action": action.description,
        "Responsable": action.assignee,
        "Echeance": action.due_date,
        "Statut": STATUS_LABELS.get(action.status, action.status),
        "Dependance": action.dependency,
        "Source": DEFAULT_SOURCE,
    }


def format_confirmation(result: SuiviResult) -> str:
    lines = ["Suivi préparé.", ""]
    lines.append(f"{len(result.analysis.decisions)} décision(s) identifiée(s).")

    if result.grist_error:
        lines.append(f"⚠️ Échec de l'ajout des actions dans Grist : {result.grist_error}")
    else:
        lines.append(f"{len(result.grist_record_ids)} action(s) ajoutée(s) dans Grist.")

    if result.docs_error:
        lines.append(f"⚠️ Échec de la création du compte-rendu dans Docs : {result.docs_error}")
    else:
        lines.append("Compte-rendu créé dans Docs.")

    if result.blockers:
        lines.extend(["", "⚠️ Point d'attention :"])
        lines.extend(result.blockers)

    return "\n".join(lines)


class MissionControlSuiviService:
    def __init__(
        self,
        analyzer: MeetingAnalyzer,
        docs_publisher,
        grist_publisher,
    ) -> None:
        self.analyzer = analyzer
        self.docs_publisher = docs_publisher
        self.grist_publisher = grist_publisher

    def organise_le_suivi(self, transcript: str) -> SuiviResult:
        analysis = self.analyzer.analyze(transcript)
        result = SuiviResult(analysis=analysis)

        try:
            self.docs_publisher(analysis)
            result.docs_document_id = getattr(
                self.docs_publisher, "last_created_document_id", None
            )
        except Exception as exc:
            result.docs_error = str(exc)

        try:
            grist_actions = [action_to_grist_fields(action) for action in analysis.actions]
            self.grist_publisher(grist_actions)
            result.grist_record_ids = list(
                getattr(self.grist_publisher, "last_created_record_ids", [])
            )
        except Exception as exc:
            result.grist_error = str(exc)

        return result
