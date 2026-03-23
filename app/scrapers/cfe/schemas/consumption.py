from dataclasses import dataclass


@dataclass
class Consumption:
    total_kwh: str
    daily_kwh: str
    type: str
