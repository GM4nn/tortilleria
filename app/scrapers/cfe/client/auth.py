"""Authentication and HTTP session against CFE Mi Espacio."""

import requests
from bs4 import BeautifulSoup

from app.scrapers.cfe.config import (
    CFE_USER,
    CFE_PASSWORD,
    LOGIN_URL,
    USER_AGENT,
)
from app.scrapers.cfe.client.aspnet import AspNetForm


class CfeSession:
    """Manages the authenticated session against the CFE portal."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    def login(self) -> bool:
        resp = self.session.get(LOGIN_URL)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        hidden_fields = AspNetForm.extract_hidden_fields(soup)

        payload = {
            **hidden_fields,
            "ctl00$MainContent$txtUsuario": CFE_USER,
            "ctl00$MainContent$txtPassword": CFE_PASSWORD,
            "ctl00$MainContent$btnIngresar": "Ingresar",
        }

        resp = self.session.post(LOGIN_URL, data=payload)
        resp.raise_for_status()

        return self.verify_login(resp)

    def verify_login(self, resp: requests.Response) -> bool:
        soup = BeautifulSoup(resp.text, "html.parser")
        error = soup.find("span", id=lambda x: x and "lblError" in x)

        return not (error and error.get_text(strip=True)) and "Login.aspx" not in resp.url

    def get(self, url: str) -> requests.Response:
        return self.session.get(url)

    def post(self, url: str, data: dict) -> requests.Response:
        return self.session.post(url, data=data)
