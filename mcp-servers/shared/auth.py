
import time
import requests


class KeycloakAuth:
    def __init__(self, keycloak_url, client_id, client_secret, username, password):
        self.token_url = f"{keycloak_url}/protocol/openid-connect/token"
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password

        self.access_token = None
        self.refresh_token = None
        self.expires_at = 0

    def _fetch_token(self, grant_type, **extra):
        data = {
            "grant_type": grant_type,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            **extra,
        }
        response = requests.post(self.token_url, data=data)
        response.raise_for_status()
        payload = response.json()

        self.access_token = payload["access_token"]
        self.refresh_token = payload.get("refresh_token")
        # petite marge de sécurité de 10s avant expiration réelle
        self.expires_at = time.time() + payload["expires_in"] - 10

        return self.access_token

    def _login(self):
        return self._fetch_token(
            "password",
            username=self.username,
            password=self.password,
            scope="openid profile email",
        )

    def _refresh(self):
        return self._fetch_token(
            "refresh_token",
            refresh_token=self.refresh_token,
        )

    def get_access_token(self):
        if self.access_token is None:
            return self._login()

        if time.time() >= self.expires_at:
            try:
                return self._refresh()
            except requests.HTTPError:
                return self._login()

        return self.access_token