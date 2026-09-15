from abc import ABC, abstractmethod

from core.models import MeetingAnalysis


class MeetingAnalyzer(ABC):
    @abstractmethod
    def analyze(self, transcript: str) -> MeetingAnalysis:
        """Analyze a meeting transcript and return structured results."""
        raise NotImplementedError

