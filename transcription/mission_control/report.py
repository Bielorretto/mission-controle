from pathlib import Path

from .analysis import MeetingAnalysis


def generate_markdown_report(analysis: MeetingAnalysis) -> str:
    """Generate a Markdown meeting report from a MeetingAnalysis."""

    lines = [
        f"# {analysis.title}",
        "",
        f"**Meeting ID:** {analysis.meeting_id}",
        f"**Language:** {analysis.language}",
        "",
        "## Summary",
        "",
        analysis.summary,
        "",
        "## Decisions",
        "",
    ]

    if analysis.decisions:
        for decision in analysis.decisions:
            lines.append(f"- {decision.description}")
    else:
        lines.append("No decisions recorded.")

    lines.extend(
        [
            "",
            "## Actions",
            "",
        ]
    )

    if analysis.actions:
        lines.extend(
            [
                "| Action | Assignee | Due date | Status |",
                "|---|---|---|---|",
            ]
        )

        for action in analysis.actions:
            assignee = action.assignee or "Unknown"
            due_date = action.due_date or "Not specified"

            lines.append(
                f"| {action.description} | "
                f"{assignee} | "
                f"{due_date} | "
                f"{action.status} |"
            )
    else:
        lines.append("No actions recorded.")

    return "\n".join(lines) + "\n"


def save_markdown_report(
    analysis: MeetingAnalysis,
    path: str | Path,
) -> Path:
    """Generate and save a Markdown meeting report."""

    output_path = Path(path)
    output_path.write_text(
        generate_markdown_report(analysis),
        encoding="utf-8",
    )

    return output_path
