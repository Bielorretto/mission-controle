from core.analysis import MeetingAnalyzer
from core.models import ActionItem, Decision, MeetingAnalysis
from core.orchestrator import MissionControlOrchestrator


class FakeMeetingAnalyzer(MeetingAnalyzer):
    def analyze(self, transcript: str) -> MeetingAnalysis:
        return MeetingAnalysis(
            meeting_id="meeting-test-001",
            title="Mission Control Test",
            language="fr",
            summary="The meeting was successfully analyzed.",
            decisions=[
                Decision(
                    description="Use Mission Control for meeting follow-up."
                )
            ],
            actions=[
                ActionItem(
                    id="action-001",
                    description="Prepare the Mission Control demo.",
                    assignee="Celine",
                    due_date=None,
                )
            ],
        )


def test_orchestrator() -> None:
    orchestrator = MissionControlOrchestrator(
        analyzer=FakeMeetingAnalyzer()
    )

    result = orchestrator.run("This is a test meeting transcript.")

    assert result.meeting_id == "meeting-test-001"
    assert len(result.decisions) == 1
    assert len(result.actions) == 1
    assert result.actions[0].status == "todo"
    