from collections.abc import Callable

from core.models import MeetingAnalysis


Analyzer = Callable[[str], MeetingAnalysis]
Publisher = Callable[[MeetingAnalysis], None]


class MissionControlOrchestrator:
    def __init__(
        self,
        analyzer: Analyzer,
        publishers: list[Publisher] | None = None,
    ) -> None:
        self.analyzer = analyzer
        self.publishers = publishers or []

    def run(self, transcript: str) -> MeetingAnalysis:
        if not transcript.strip():
            raise ValueError("Transcript cannot be empty.")

        analysis = self.analyzer(transcript)

        for publisher in self.publishers:
            publisher(analysis)

        return analysis
