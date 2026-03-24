"""Orchestrator: authentication -> download -> parsing -> return invoices."""

import xml.etree.ElementTree as ET

from app.scrapers.cfe.client import CfeSession, InvoicesClient
from app.scrapers.cfe.parsers import CfdiParser
from app.scrapers.cfe.schemas import Invoice


def scrape_cfe(user: str, password: str) -> list[Invoice]:
    """Run the full CFE scraping pipeline with the given credentials."""

    # Step 1: Authentication
    cfe = CfeSession(user, password)
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
