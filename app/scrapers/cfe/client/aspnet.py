"""Utilities for interacting with ASP.NET forms (ViewState, PostBack)."""

import re
from bs4 import BeautifulSoup


class AspNetForm:
    """Extracts hidden fields and parses PostBack events from ASP.NET pages."""

    @staticmethod
    def extract_hidden_fields(soup: BeautifulSoup) -> dict:
        fields = {}
        for tag in soup.find_all("input", attrs={"type": "hidden"}):
            name = tag.get("name")
            if name:
                fields[name] = tag.get("value", "")
        return fields

    @staticmethod
    def parse_postback(href: str) -> tuple[str, str] | None:
        match = re.search(r"__doPostBack\('([^']+)','([^']*)'\)", href)
        if match:
            return match.group(1), match.group(2)
        return None
