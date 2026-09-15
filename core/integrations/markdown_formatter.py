from core.models import ActionItem, MeetingAnalysis


def format_meeting_analysis_as_markdown(analysis: MeetingAnalysis) -> str:
    lines = [
        f"# {analysis.title}",
        "",
        "## Résumé",
        analysis.summary,
        "",
        "## Décisions",
    ]

    if analysis.decisions:
        lines.extend(f"- {decision.description}" for decision in analysis.decisions)
    else:
        lines.append("- Aucune décision enregistrée.")

    lines.extend(["", "## Actions"])

    if analysis.actions:
        lines.extend(_format_action(action) for action in analysis.actions)
    else:
        lines.append("- Aucune action enregistrée.")

    return "\n".join(lines) + "\n"


def _format_action(action: ActionItem) -> str:
    assignee = action.assignee or "Non assigné"
    due_date = action.due_date or "Non définie"
    return f"- [ ] {action.description} — Responsable: {assignee} — Échéance: {due_date}"
