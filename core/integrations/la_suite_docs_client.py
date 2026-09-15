import httpx


def create_document_for_owner(
    base_url: str,
    token: str,
    title: str,
    content: str,
    sub: str,
    email: str,
    timeout: float = 30.0,
) -> dict:
    response = httpx.post(
        f"{base_url}/documents/create-for-owner/",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        json={
            "title": title,
            "content": content,
            "sub": sub,
            "email": email,
        },
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()
