from dataclasses import dataclass


@dataclass
class Period:
    date_from: str
    date_to: str
    days: str
    payment_due_date: str
    cutoff_date: str
