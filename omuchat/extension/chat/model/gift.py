from typing import TypedDict

from omuchat.interface.model import Model


class GiftJson(TypedDict):
    id: str
    name: str
    amount: int
    image_url: str
    is_paid: bool


class Gift(Model[GiftJson]):
    def __init__(
        self, id: str, name: str, amount: int, image_url: str, is_paid: bool
    ) -> None:
        self.id = id
        self.name = name
        self.amount = amount
        self.image_url = image_url
        self.is_paid = is_paid

    @classmethod
    def from_json(cls, json: GiftJson) -> "Gift":
        return cls(
            id=json["id"],
            name=json["name"],
            amount=json["amount"],
            image_url=json["image_url"],
            is_paid=json["is_paid"],
        )

    def json(self) -> GiftJson:
        return {
            "id": self.id,
            "name": self.name,
            "amount": self.amount,
            "image_url": self.image_url,
            "is_paid": self.is_paid,
        }

    def __str__(self) -> str:
        return self.name
