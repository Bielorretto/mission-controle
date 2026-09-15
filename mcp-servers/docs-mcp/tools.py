# docs-mcp/tools.py
import os
import requests
from dotenv import load_dotenv
from shared.auth import KeycloakAuth

load_dotenv()

DOCS_API_URL = "http://localhost:8071/api/v1.0"

auth = KeycloakAuth(
    keycloak_url=os.environ["KEYCLOAK_URL"],
    client_id=os.environ["KEYCLOAK_CLIENT_ID"],
    client_secret=os.environ["KEYCLOAK_CLIENT_SECRET"],
    username=os.environ["KEYCLOAK_USERNAME"],
    password=os.environ["KEYCLOAK_PASSWORD"],
)


def create_document(title: str) -> dict:
    token = auth.get_access_token()

    response = requests.post(
        f"{DOCS_API_URL}/documents/",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={"title": title},
    )
    print(response.status_code, response.text) 
    response.raise_for_status()

    return response.json()



if __name__ == "__main__":
    doc = create_document("Mon premier document via MCP")
    print(doc)