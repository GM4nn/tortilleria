"""Configuration and constants for the CFE scraper."""


# Credentials
CFE_USER = "germancodeg1"
CFE_PASSWORD = "Lomismoxd123%"

# URLs
LOGIN_URL = "https://app.cfe.mx/Aplicaciones/CCFE/MiEspacio/Login.aspx"
INVOICES_URL = "https://app.cfe.mx/Aplicaciones/CCFE/MiEspacio/OtrasFacturas.aspx"

# Filters
INVOICE_TYPE_FILTER = "OCR"

# Parser
NAMESPACE_CFDI_DEFAULT = "http://www.sat.gob.mx/cfd/4"

# HTTP Headers
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
