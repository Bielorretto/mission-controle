import argparse
import dataclasses
import json
import sys

from core.ollama_analyzer import OllamaMeetingAnalyzer
from core.orchestrator import MissionControlOrchestrator


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a meeting transcript through Mission Control."
    )
    parser.add_argument(
        "transcript_path",
        help="Path to a transcript text file.",
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:11434/v1",
        help="Ollama-compatible base URL (default: %(default)s).",
    )
    parser.add_argument(
        "--model",
        default="gemma4:12b-mlx",
        help="Model name to use (default: %(default)s).",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    with open(args.transcript_path, encoding="utf-8") as f:
        transcript = f.read()

    analyzer = OllamaMeetingAnalyzer(base_url=args.base_url, model=args.model)
    orchestrator = MissionControlOrchestrator(analyzer=analyzer)

    analysis = orchestrator.run(transcript)

    print(json.dumps(dataclasses.asdict(analysis), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
