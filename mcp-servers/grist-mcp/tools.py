# grist-mcp/tools.py
#
# Read-only Grist access for Mission Control. No capability like this existed
# anywhere in the repo before (core/integrations/grist_client.py only ever
# supported creating records). This is intentionally generic — it exposes raw
# table data and lets the agent reason over it, rather than baking in any
# demo-specific statistics logic here.

import os

import httpx
from dotenv import load_dotenv

load_dotenv()

DEFAULT_BASE_URL = "http://localhost:8484"
DEFAULT_TABLE_ID = "Table1"


def _config():
    base_url = os.environ.get("GRIST_BASE_URL", DEFAULT_BASE_URL)
    api_key = os.environ["GRIST_API_KEY"]
    doc_id = os.environ["GRIST_DOC_ID"]
    default_table_id = os.environ.get("GRIST_TABLE_ID", DEFAULT_TABLE_ID)
    return base_url, api_key, doc_id, default_table_id


def list_tables() -> list:
    """List the tables available in the configured Grist document, with their
    column ids — useful to inspect the schema before querying records."""
    base_url, api_key, doc_id, _ = _config()

    tables_response = httpx.get(
        f"{base_url}/api/docs/{doc_id}/tables",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=30.0,
    )
    tables_response.raise_for_status()
    tables = [t["id"] for t in tables_response.json().get("tables", [])]

    result = []
    for table_id in tables:
        columns_response = httpx.get(
            f"{base_url}/api/docs/{doc_id}/tables/{table_id}/columns",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0,
        )
        columns_response.raise_for_status()
        columns = [c["id"] for c in columns_response.json().get("columns", [])]
        result.append({"table_id": table_id, "columns": columns})

    return result


def get_records(table_id: str = None) -> list:
    """Fetch all records from a Grist table (defaults to the configured
    demo table if table_id is omitted). Returns each record's id and fields,
    as-is — no aggregation or filtering is applied here."""
    base_url, api_key, doc_id, default_table_id = _config()
    table_id = table_id or default_table_id

    response = httpx.get(
        f"{base_url}/api/docs/{doc_id}/tables/{table_id}/records",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=30.0,
    )
    response.raise_for_status()
    records = response.json().get("records", [])
    return [{"id": r["id"], **r.get("fields", {})} for r in records]
