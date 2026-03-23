from dataclasses import dataclass


@dataclass
class AccountHolder:
    name: str
    address: str
    city: str
    state: str
    usage: str
