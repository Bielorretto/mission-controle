from dataclasses import dataclass


@dataclass(frozen=True)
class Transcript:
    path: str
    content: str
    format: str
