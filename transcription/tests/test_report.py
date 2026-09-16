from mission_control.analysis import Action, Decision, MeetingAnalysis
from mission_control.report import generate_markdown_report, save_markdown_report


def test_generate_markdown_report():
    analysis = MeetingAnalysis(
        meeting_id="meeting-2026-09-15-001",
        title="Project Alpha",
        language="en",
        summary="The team reviewed the progress of Project Alpha.",
        decisions=[
            Decision(description="Keep the new architecture."),
            Decision(
                description="Continue performance testing before production."
            ),
        ],
        actions=[
            Action(
                id="action-001",
                description="Optimize the slowest requests.",
                assignee="Diouf",
                due_date="2026-09-18",
                status="todo",
            ),
        ],
    )

    report = generate_markdown_report(analysis)

    assert "# Project Alpha" in report
    assert "**Meeting ID:** meeting-2026-09-15-001" in report
    assert "**Language:** en" in report
    assert "## Summary" in report
    assert "The team reviewed the progress of Project Alpha." in report
    assert "## Decisions" in report
    assert "- Keep the new architecture." in report
    assert "## Actions" in report
    assert "Optimize the slowest requests." in report
    assert "Diouf" in report
    assert "2026-09-18" in report
    assert "todo" in report


def test_generate_markdown_report_handles_missing_action_information():
    analysis = MeetingAnalysis(
        meeting_id="meeting-2026-09-15-002",
        title="Team Planning",
        language="en",
        summary="The team discussed the next development tasks.",
        decisions=[],
        actions=[
            Action(
                id="action-001",
                description="Prepare the next meeting.",
                assignee=None,
                due_date=None,
                status="todo",
            ),
        ],
    )

    report = generate_markdown_report(analysis)

    assert "No decisions recorded." in report
    assert "Prepare the next meeting." in report
    assert "Unknown" in report
    assert "Not specified" in report


def test_generate_markdown_report_handles_empty_lists():
    analysis = MeetingAnalysis(
        meeting_id="meeting-2026-09-15-003",
        title="Empty Meeting",
        language="en",
        summary="No decisions or actions were recorded.",
        decisions=[],
        actions=[],
    )

    report = generate_markdown_report(analysis)

    assert "No decisions recorded." in report
    assert "No actions recorded." in report


def test_save_markdown_report(tmp_path):
    analysis = MeetingAnalysis(
        meeting_id="meeting-2026-09-15-004",
        title="Project Alpha",
        language="en",
        summary="The team reviewed the project.",
        decisions=[
            Decision(description="Continue development."),
        ],
        actions=[
            Action(
                id="action-001",
                description="Prepare the next report.",
                assignee="Souhil",
                due_date="2026-09-20",
                status="todo",
            ),
        ],
    )

    output_path = tmp_path / "meeting_report.md"

    result = save_markdown_report(analysis, output_path)

    assert result == output_path
    assert output_path.exists()

    content = output_path.read_text(encoding="utf-8")

    assert "# Project Alpha" in content
    assert "The team reviewed the project." in content
    assert "Continue development." in content
    assert "Prepare the next report." in content
    assert "Souhil" in content
    assert "2026-09-20" in content
