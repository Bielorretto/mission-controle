import os

from core.integrations.grist_client import create_records

DEFAULT_BASE_URL = "http://localhost:8484"
DEFAULT_TABLE_ID = "Table1"


class GristPublisher:
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        doc_id: str | None = None,
        table_id: str | None = None,
    ) -> None:
        self.base_url = base_url or os.environ.get("GRIST_BASE_URL", DEFAULT_BASE_URL)
        self.api_key = api_key or os.environ["GRIST_API_KEY"]
        self.doc_id = doc_id or os.environ["GRIST_DOC_ID"]
        self.table_id = table_id or os.environ.get("GRIST_TABLE_ID", DEFAULT_TABLE_ID)
        self.last_created_record_ids: list[int] = []

    def __call__(self, actions: list[dict]) -> None:
        records = [
            {
                "Action": action["Action"],
                "Responsable": action.get("Responsable"),
                "Echeance": action.get("Echeance"),
                "Statut": action.get("Statut"),
                "Dependance": action.get("Dependance"),
                "Source": action.get("Source"),
            }
            for action in actions
        ]

        result = create_records(
            base_url=self.base_url,
            api_key=self.api_key,
            doc_id=self.doc_id,
            table_id=self.table_id,
            records=records,
        )

        self.last_created_record_ids = [record["id"] for record in result.get("records", [])]
