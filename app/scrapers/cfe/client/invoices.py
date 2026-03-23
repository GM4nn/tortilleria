"""Navigation and XML download of invoices from OtrasFacturas.aspx."""

from bs4 import BeautifulSoup

from app.scrapers.cfe.config import INVOICES_URL, INVOICE_TYPE_FILTER
from app.scrapers.cfe.client.auth import CfeSession
from app.scrapers.cfe.client.aspnet import AspNetForm

TABLE_ID = "ctl00_MainContent_gvFacturasUsuario"


class InvoicesClient:
    """Navigates to the invoices page, filters rows, and downloads XMLs."""

    def __init__(self, cfe_session: CfeSession):
        self.cfe = cfe_session

    def fetch_xmls(self) -> list[bytes]:
        type_filter = INVOICE_TYPE_FILTER
        resp = self.cfe.get(INVOICES_URL)
        resp.raise_for_status()

        if "Login.aspx" in resp.url:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table", id=TABLE_ID)

        if not table:
            return []

        type_col = self.find_type_column(table)
        if type_col is None:
            return []

        rows = self.filter_rows(table, type_col, type_filter)

        return self.download_xmls(rows, soup)

    def find_type_column(self, table) -> int | None:
        header = table.find("tr")
        headers = [th.get_text(strip=True).lower() for th in header.find_all(["th", "td"])]

        for i, h in enumerate(headers):
            if "tipo" in h:
                return i
        return None

    def filter_rows(self, table, type_col: int, type_filter: str) -> list:
        result = []

        for row in table.find_all("tr")[1:]:
            cells = row.find_all("td")
            if not cells or type_col >= len(cells):
                continue

            row_type = cells[type_col].get_text(strip=True).upper()
            if row_type != type_filter.upper():
                continue

            link = self.find_xml_link(row)
            if link:
                result.append(link)

        return result

    def find_xml_link(self, row):
        for a_tag in row.find_all("a", href=True):
            text = a_tag.get_text(strip=True).lower()
            href = a_tag["href"]
            if "xml" in text or "xml" in href.lower():
                return a_tag

        for a_tag in row.find_all("a", href=True):
            if "__doPostBack" in a_tag.get("href", ""):
                return a_tag

        return None

    def download_xmls(self, links: list, soup) -> list[bytes]:
        xmls = []

        for link in links:
            xml_bytes = self.download_xml(link, soup)
            if xml_bytes:
                xmls.append(xml_bytes)

        return xmls

    def download_xml(self, link, soup) -> bytes | None:
        href = link.get("href", "")

        if href.startswith("http") or href.startswith("/"):
            url = href if href.startswith("http") else f"https://app.cfe.mx{href}"
            r = self.cfe.get(url)
            r.raise_for_status()
            return r.content

        if "__doPostBack" in href:
            postback = AspNetForm.parse_postback(href)
            if not postback:
                return None

            fields = AspNetForm.extract_hidden_fields(soup)
            payload = {
                **fields,
                "__EVENTTARGET": postback[0],
                "__EVENTARGUMENT": postback[1],
            }

            r = self.cfe.post(INVOICES_URL, data=payload)
            r.raise_for_status()

            content_type = r.headers.get("Content-Type", "")
            content_disp = r.headers.get("Content-Disposition", "")

            if "xml" in content_type or "octet" in content_type or "attachment" in content_disp:
                return r.content

        return None
