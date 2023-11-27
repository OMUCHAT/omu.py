from datetime import datetime
from typing import TypedDict

from omu.interface.keyable import Keyable
from omu.interface.model import Model

from .author import Author, AuthorJson
from .content import Content, ContentComponent, ContentJson
from .gift import Gift, GiftJson
from .paid import Paid, PaidJson


class MessageJson(TypedDict):
    room_id: str
    id: str
    content: ContentJson | None
    author: AuthorJson | None
    paid: PaidJson | None
    gift: GiftJson | None
    created_at: int | None


class Message(Keyable, Model[MessageJson]):
    def __init__(
        self,
        room_id: str,
        id: str,
        content: Content | None = None,
        author: Author | None = None,
        paid: Paid | None = None,
        gift: Gift | None = None,
        created_at: datetime | None = None,
    ) -> None:
        self.room_id = room_id
        self.id = id
        self.content = content
        self.author = author
        self.paid = paid
        self.gift = gift
        self.created_at = created_at

    @classmethod
    def from_json(cls, json: MessageJson) -> "Message":
        return cls(
            room_id=json["room_id"],
            id=json["id"],
            content=ContentComponent.from_json(json["content"])
            if json["content"]
            else None,
            author=Author.from_json(json["author"]) if json["author"] else None,
            paid=Paid.from_json(json["paid"]) if json["paid"] else None,
            gift=Gift.from_json(json["gift"]) if json["gift"] else None,
            created_at=datetime.fromtimestamp(json["created_at"] / 1000)
            if json["created_at"]
            else None,
        )

    def key(self) -> str:
        return self.id

    def json(self) -> MessageJson:
        return MessageJson(
            room_id=self.room_id,
            id=self.id,
            content=self.content.json() if self.content else None,
            author=self.author.json() if self.author else None,
            paid=self.paid.json() if self.paid else None,
            gift=self.gift.json() if self.gift else None,
            created_at=int(self.created_at.timestamp() * 1000)
            if self.created_at
            else None,
        )

    def __str__(self) -> str:
        return f"{self.author}: {self.content}"
