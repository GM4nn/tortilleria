from dataclasses import dataclass

from app.scrapers.cfe.schemas.period import Period
from app.scrapers.cfe.schemas.consumption import Consumption
from app.scrapers.cfe.schemas.charge import Charge
from app.scrapers.cfe.schemas.account_holder import AccountHolder


@dataclass
class Invoice:
    series: str
    folio: str
    date: str
    rpu: str
    rate: str
    service_type: str
    account_holder: AccountHolder
    period: Period
    consumption: Consumption
    charge: Charge
