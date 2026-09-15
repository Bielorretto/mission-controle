from dataclasses import dataclass


@dataclass
class ActionItem:
    id: str
    description: str
    assignee: str | None
    due_date: str | None
    status: str = "todo"

@dataclass
class Decision:
    description: str

@dataclass
class MeetingAnalysis:
    meeting_id: str
    title: str
    language: str
    summary: str
    decisions: list[Decision]
    actions: list[ActionItem]