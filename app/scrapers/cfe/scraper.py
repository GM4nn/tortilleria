"""Orchestrator: authentication -> download -> parsing -> presentation."""

import xml.etree.ElementTree as ET

from app.scrapers.cfe.client import CfeSession, InvoicesClient
from app.scrapers.cfe.parsers import CfdiParser
from app.scrapers.cfe.schemas import Invoice


def main() -> list[Invoice]:
    """Run the full CFE scraping pipeline and return parsed invoices."""

    # Step 1: Authentication
    cfe = CfeSession()
    if not cfe.login():
        return []

    # Step 2: Download XMLs
    client = InvoicesClient(cfe)
    xmls = client.fetch_xmls()

    if not xmls:
        return []

    # Step 3: Parse XMLs into Invoice objects
    parser = CfdiParser()
    invoices: list[Invoice] = []

    for xml_bytes in xmls:
        try:
            invoices.append(parser.parse(xml_bytes))
        except ET.ParseError:
            pass

    return invoices
