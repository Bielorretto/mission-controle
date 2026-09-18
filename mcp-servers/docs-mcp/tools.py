# docs-mcp/tools.py
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv
from shared.auth import KeycloakAuth

_DOCS_MCP_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _DOCS_MCP_DIR.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

load_dotenv()
load_dotenv(_DOCS_MCP_DIR / ".env")

DOCS_API_URL = "http://localhost:18071/external_api/v1.0"

auth = KeycloakAuth(
    keycloak_url=os.environ["KEYCLOAK_URL"],
    client_id=os.environ["KEYCLOAK_CLIENT_ID"],
    client_secret=os.environ["KEYCLOAK_CLIENT_SECRET"],
    username=os.environ["KEYCLOAK_USERNAME"],
    password=os.environ["KEYCLOAK_PASSWORD"],
)


def create_document(title: str, content: str = None) -> dict:
    token = auth.get_access_token()

    if content:
        # Docs converts an uploaded file into the document's initial Yjs content,
        # but also overwrites the title with the uploaded file's name (which must
        # end in .md or .docx) — so restore the intended title with a follow-up patch.
        response = requests.post(
            f"{DOCS_API_URL}/documents/",
            headers={"Authorization": f"Bearer {token}"},
            data={"title": title},
            files={"file": (f"{title}.md", content.encode("utf-8"), "text/markdown")},
        )
        response.raise_for_status()
        doc = response.json()
        fix_response = requests.patch(
            f"{DOCS_API_URL}/documents/{doc['id']}/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={"title": title},
        )
        fix_response.raise_for_status()
        return fix_response.json()
    else:
        response = requests.post(
            f"{DOCS_API_URL}/documents/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={"title": title},
        )
    response.raise_for_status()
    return response.json()


def list_documents(title: str = None) -> list:
    token = auth.get_access_token()

    params = {"title": title} if title else {}
    response = requests.get(
        f"{DOCS_API_URL}/documents/",
        headers={"Authorization": f"Bearer {token}"},
        params=params,
    )
    response.raise_for_status()
    data = response.json()
    results = data.get("results", data)
    return [{"id": doc["id"], "title": doc["title"]} for doc in results]


def delete_document(document_id: str) -> dict:
    token = auth.get_access_token()

    response = requests.delete(
        f"{DOCS_API_URL}/documents/{document_id}/",
        headers={"Authorization": f"Bearer {token}"},
    )
    response.raise_for_status()
    return {"deleted": True, "id": document_id}


def _markdown_to_yjs_base64(token: str, content: str) -> str:
    """Convert markdown to Yjs content by round-tripping through a throwaway
    document — Docs only exposes markdown->Yjs conversion via document creation."""
    create_response = requests.post(
        f"{DOCS_API_URL}/documents/",
        headers={"Authorization": f"Bearer {token}"},
        data={"title": "__mcp_content_conversion_tmp__"},
        files={"file": ("__mcp_content_conversion_tmp__.md", content.encode("utf-8"), "text/markdown")},
    )
    create_response.raise_for_status()
    tmp_doc_id = create_response.json()["id"]

    try:
        content_response = requests.get(
            f"{DOCS_API_URL}/documents/{tmp_doc_id}/content/",
            headers={"Authorization": f"Bearer {token}"},
        )
        content_response.raise_for_status()
        # Docs stores the content as the base64 string itself (as utf-8 text),
        # not raw Yjs bytes — no re-encoding needed here.
        return content_response.content.decode("utf-8")
    finally:
        requests.delete(
            f"{DOCS_API_URL}/documents/{tmp_doc_id}/",
            headers={"Authorization": f"Bearer {token}"},
        )


def write_document(document_id: str, content: str) -> dict:
    """Replace the full content of an existing document with new text/markdown."""
    token = auth.get_access_token()

    yjs_content_b64 = _markdown_to_yjs_base64(token, content)

    response = requests.patch(
        f"{DOCS_API_URL}/documents/{document_id}/content/",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        # `websocket: True` tells Docs this write doesn't need the "no active
        # collaborative session" safety check — appropriate for a one-shot API
        # write, not a live collaborative editor.
        json={"content": yjs_content_b64, "websocket": True},
    )
    response.raise_for_status()
    return {"updated": True, "id": document_id}


def read_document(document_id: str) -> dict:
    """Get a document's title and content as markdown, for the agent to
    paste/summarize."""
    token = auth.get_access_token()

    response = requests.get(
        f"{DOCS_API_URL}/documents/{document_id}/formatted-content/",
        headers={"Authorization": f"Bearer {token}"},
        params={"content_format": "markdown"},
    )
    response.raise_for_status()
    data = response.json()
    return {"id": data["id"], "title": data["title"], "content": data["content"]}


def share_document(document_id: str, reach: str = "authenticated", role: str = "reader") -> dict:
    """Share a document via a link. `reach`: restricted/authenticated/public.
    `role`: reader/commenter/editor."""
    token = auth.get_access_token()

    response = requests.put(
        f"{DOCS_API_URL}/documents/{document_id}/link-configuration/",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={"link_reach": reach, "link_role": role},
    )
    response.raise_for_status()
    return response.json()


def create_document_as_owner(title: str, content: str) -> dict:
    """Create a document via the server-to-server create-for-owner API,
    owned by the configured LA_SUITE_DOCS_OWNER_SUB/EMAIL user (the demo
    "impress" account). Unlike create_document() above (which authenticates
    via Keycloak and requires OIDC resource-server auth to be enabled on the
    Docs backend), this reuses the same already-validated path Mission
    Control's own suivi workflow uses, so it works against this environment
    as-is."""
    from core.integrations.la_suite_docs_client import create_document_for_owner

    base_url = os.environ.get(
        "LA_SUITE_DOCS_BASE_URL", "http://localhost:18071/api/v1.0"
    )
    token = os.environ["LA_SUITE_DOCS_TOKEN"]
    owner_sub = os.environ["LA_SUITE_DOCS_OWNER_SUB"]
    owner_email = os.environ["LA_SUITE_DOCS_OWNER_EMAIL"]

    result = create_document_for_owner(
        base_url=base_url,
        token=token,
        title=title,
        content=content,
        sub=owner_sub,
        email=owner_email,
    )
    return {"id": result["id"], "title": title}


def _server_to_server_config():
    base_url = os.environ.get(
        "LA_SUITE_DOCS_BASE_URL", "http://localhost:18071/api/v1.0"
    )
    token = os.environ["LA_SUITE_DOCS_TOKEN"]
    owner_sub = os.environ["LA_SUITE_DOCS_OWNER_SUB"]
    return base_url, token, owner_sub


def search_documents_as_owner(title: str = None) -> list:
    """List/search documents accessible to the configured owner
    (LA_SUITE_DOCS_OWNER_SUB), optionally filtered by a title substring.
    Uses the same server-to-server path as create_document_as_owner, so it
    works against this environment as-is (no Keycloak resource-server auth
    required)."""
    base_url, token, owner_sub = _server_to_server_config()

    params = {"sub": owner_sub}
    if title:
        params["title"] = title

    response = requests.get(
        f"{base_url}/documents/list-for-owner/",
        headers={"Authorization": f"Bearer {token}"},
        params=params,
    )
    response.raise_for_status()
    return response.json()


def get_document_content_as_owner(document_id: str) -> dict:
    """Read a document's actual title and content (as markdown), scoped to
    the configured owner. Returns only documents that owner actually has
    access to. Uses the same server-to-server path as
    create_document_as_owner."""
    base_url, token, owner_sub = _server_to_server_config()

    response = requests.get(
        f"{base_url}/documents/{document_id}/content-for-owner/",
        headers={"Authorization": f"Bearer {token}"},
        params={"sub": owner_sub},
    )
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    doc = create_document("Mon premier document via MCP")
    print(doc)