import json

import httpx

from core.analysis import MeetingAnalyzer
from core.models import ActionItem, Decision, MeetingAnalysis

SYSTEM_PROMPT = """
You are Mission Control, an AI assistant for public-sector meetings.

Analyze the meeting transcript and return ONLY valid JSON.
Do not include Markdown, explanations, or text outside the JSON.

The JSON must follow exactly this structure:

{
  "meeting_id": "string",
  "title": "string",
  "language": "string",
  "summary": "string",
  "decisions": [
    {
      "description": "string"
    }
  ],
  "actions": [
    {
      "id": "string",
      "description": "string",
      "assignee": "string or null",
      "due_date": "string or null",
      "status": "todo",
      "dependency": "string or null"
    }
  ]
}

Rules:
- Detect the language of the meeting.
- Write the summary in the language of the meeting.
- Extract only decisions actually made during the meeting.
- Extract only actionable tasks actually mentioned.
- Do not invent an assignee or due date.
- Use null when an assignee or due date is unknown.
- Every action must have status "todo".
- If an action depends on, or blocks, another action mentioned in the meeting,
  describe that relationship in "dependency" (e.g. "Depends on the list being
  sent on Wednesday"). Use null when there is no such relationship.
"""

class OllamaMeetingAnalyzer(MeetingAnalyzer):
    def __init__(
        self,
        base_url: str = "http://localhost:11434/v1",
        model: str = "gemma4:12b-mlx",
    ) -> None:
        self.base_url = base_url
        self.model = model

    def analyze(self, transcript: str) -> MeetingAnalysis:
        if not transcript.strip():
            raise ValueError("Transcript cannot be empty.")

        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer ollama",
            },
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": transcript,
                    },
                ],
            },
            timeout=300.0,
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]

        parsed = json.loads(content)

        decisions = [
            Decision(
                description=decision["description"],
            )
            for decision in parsed["decisions"]
        ]

        actions = [
            ActionItem(
                id=action["id"],
                description=action["description"],
                assignee=action.get("assignee"),
                due_date=action.get("due_date"),
                status=action.get("status", "todo"),
                dependency=action.get("dependency"),
            )
            for action in parsed["actions"]
        ]

        return MeetingAnalysis(
            meeting_id=parsed["meeting_id"],
            title=parsed["title"],
            language=parsed["language"],
            summary=parsed["summary"],
            decisions=decisions,
            actions=actions,
        )
