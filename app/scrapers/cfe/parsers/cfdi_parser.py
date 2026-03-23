"""Parsing of CFE CFDI XMLs to extract billing data."""

import re
import xml.etree.ElementTree as ET

from app.scrapers.cfe.schemas import Invoice, Period, Consumption, Charge, AccountHolder
from app.scrapers.cfe.config import NAMESPACE_CFDI_DEFAULT

class CfdiParser:
    """Converts a CFE CFDI XML into an Invoice object."""

    def parse(self, xml_bytes: bytes) -> Invoice:
        root = ET.fromstring(xml_bytes)
        ns = self.detect_namespace(root)

        tax = "0"
        tax_node = root.find(f".//{{{ns}}}Impuestos")
        if tax_node is not None:
            tax = tax_node.get("TotalImpuestosTrasladados", "0")

        addenda = root.find(f".//{{{ns}}}Addenda")
        record = None
        if addenda is not None:
            record = addenda.find(".//clsRegArchFact")

        return Invoice(
            series=root.get("Serie", ""),
            folio=root.get("Folio", ""),
            date=root.get("Fecha", ""),
            rpu=self.text(record, "RPU"),
            rate=self.text(record, "TARIFA"),
            service_type=self.text(record, "Med_TipoServ"),
            account_holder=AccountHolder(
                name=self.text(record, "NOMBRE"),
                address=self.text(record, "DIRECC"),
                city=self.text(record, "NOMPOB"),
                state=self.text(record, "NOMEST"),
                usage=self.text(record, "Uso"),
            ),
            period=Period(
                date_from=self.text(record, "FECDESDE"),
                date_to=self.text(record, "FECHASTA"),
                days=self.text(record, "Dias"),
                payment_due_date=self.text(record, "FECLIMITE"),
                cutoff_date=self.text(record, "FECORTE"),
            ),
            consumption=Consumption(
                total_kwh=self.text(record, "CONSUMO_R"),
                daily_kwh=self.text(record, "ConsumoDiario"),
                type=self.text(record, "TipoDeConsumo"),
            ),
            charge=Charge(
                subtotal=root.get("SubTotal", ""),
                tax=tax,
                dap=self.text(record, "IMPDAP"),
                total=root.get("Total", ""),
                currency=root.get("Moneda", "MXN"),
                daily_price=self.text(record, "PrecioDiario"),
            ),
        )

    def detect_namespace(self, root: ET.Element) -> str:
        match = re.match(r"\{(.+?)\}", root.tag)
        return match.group(1) if match else NAMESPACE_CFDI_DEFAULT

    def text(self, node, tag: str, default: str = "") -> str:
        if node is None:
            return default
        el = node.find(tag)
        if el is not None and el.text:
            return el.text.strip()
        return default
