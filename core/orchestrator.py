from collections.abc import Callable

from core.analysis import MeetingAnalyzer
from core.models import MeetingAnalysis


Publisher = Callable[[MeetingAnalysis], None]


class MissionControlOrchestrator:
    def __init__(
        self,
        analyzer: MeetingAnalyzer,
        publishers: list[Publisher] | None = None,
    ) -> None:
        self.analyzer = analyzer
        self.publishers = publishers or []

    def run(self, transcript: str) -> MeetingAnalysis:
        if not transcript.strip():
            raise ValueError("Transcript cannot be empty.")

        analysis = self.analyzer.analyze(transcript)

        for publisher in self.publishers:
            publisher(analysis)

        return analysis