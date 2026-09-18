"""Manual smoke test — NOT run automatically.

Publishes exactly ONE clearly-labelled test record to the locally running
Grist instance, using the real GristPublisher. Never updates or deletes any
existing record; never prints credential values.

Requires these environment variables to be set (never hardcode them):
    GRIST_BASE_URL   (optional, defaults to http://localhost:8484)
    GRIST_API_KEY
    GRIST_DOC_ID
    GRIST_TABLE_ID   (optional, defaults to Table1)

Usage:
    python3 scripts/smoke_test_publish_to_grist.py
"""

import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.integrations.grist_publisher import GristPublisher


def main(argv: list[str]) -> int:
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    action = {
        "Action": f"[Mission Control SMOKE TEST] {timestamp}",
        "Responsable": "Mission Control",
        "Echeance": "N/A",
        "Statut": "À faire",
        "Dependance": "Aucune",
        "Source": "smoke_test_publish_to_grist.py",
    }

    publisher = GristPublisher()
    publisher([action])

    print("Smoke test record published successfully.")
    print(f"Action:      {action['Action']}")
    print(f"Record IDs:  {publisher.last_created_record_ids}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
