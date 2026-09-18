import httpx


def create_records(
    base_url: str,
    api_key: str,
    doc_id: str,
    table_id: str,
    records: list[dict],
    timeout: float = 30.0,
) -> dict:
    response = httpx.post(
        f"{base_url}/api/docs/{doc_id}/tables/{table_id}/records",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        json={"records": [{"fields": fields} for fields in records]},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()
