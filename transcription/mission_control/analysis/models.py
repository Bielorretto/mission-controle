from dataclasses import dataclass


@dataclass(frozen=True)
class Decision:
    description: str


@dataclass(frozen=True)
class Action:
    id: str
    description: str
    assignee: str | None
    due_date: str | None
    status: str


@dataclass(frozen=True)
class MeetingAnalysis:
    meeting_id: str
    title: str
    language: str
    summary: str
    decisions: list[Decision]
    actions: list[Action]
