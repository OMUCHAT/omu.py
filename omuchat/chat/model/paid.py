from typing import TypedDict

from omu.interface.model import Model


class PaidJson(TypedDict):
    amount: int
    currency: str


class Paid(Model[PaidJson]):
    def __init__(self, amount: int, currency: str) -> None:
        self.amount = amount
        self.currency = currency

    @classmethod
    def from_json(cls, json: PaidJson) -> "Paid":
        return cls(amount=json["amount"], currency=json["currency"])

    def json(self) -> PaidJson:
        return {"amount": self.amount, "currency": self.currency}

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"
