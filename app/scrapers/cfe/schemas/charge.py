from dataclasses import dataclass


@dataclass
class Charge:
    subtotal: str
    tax: str
    dap: str
    total: str
    currency: str
    daily_price: str
