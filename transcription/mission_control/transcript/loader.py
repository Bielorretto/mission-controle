from pathlib import Path

from .models import Transcript


SUPPORTED_EXTENSIONS = {".txt", ".md"}


def load_transcript(path: str | Path) -> Transcript:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Transcript file not found: {path}")

    if not file_path.is_file():
        raise ValueError(f"Transcript path is not a file: {path}")

    extension = file_path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported transcript format: {extension}"
        )

    content = file_path.read_text(encoding="utf-8")

    if not content.strip():
        raise ValueError("Transcript is empty")

    return Transcript(
        path=str(file_path),
        content=content,
        format=extension[1:],
    )
