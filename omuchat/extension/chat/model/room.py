from typing import TypedDict

from omuchat.interface.keyable import Keyable
from omuchat.interface.model import Model


class RoomJson(TypedDict):
    id: str
    provider_id: str
    channel_id: str | None
    name: str
    description: str | None
    online: int
    url: str
    image_url: str | None
    viewers: int | None


class Room(Keyable, Model[RoomJson]):
    def __init__(
        self,
        id: str,
        provider_id: str,
        channel_id: str | None,
        name: str,
        description: str | None,
        online: int,
        url: str,
        image_url: str | None,
        viewers: int | None,
    ) -> None:
        self.id = id
        self.provider_id = provider_id
        self.channel_id = channel_id
        self.name = name
        self.description = description
        self.online = online
        self.url = url
        self.image_url = image_url
        self.viewers = viewers

    @classmethod
    def from_json(cls, json: RoomJson) -> "Room":
        return cls(
            id=json["id"],
            provider_id=json["provider_id"],
            channel_id=json["channel_id"],
            name=json["name"],
            description=json["description"],
            online=json["online"],
            url=json["url"],
            image_url=json["image_url"],
            viewers=json["viewers"],
        )

    def key(self) -> str:
        return f"{self.id}@{self.provider_id}"

    def json(self) -> RoomJson:
        return RoomJson(
            id=self.id,
            provider_id=self.provider_id,
            channel_id=self.channel_id,
            name=self.name,
            description=self.description,
            online=self.online,
            url=self.url,
            image_url=self.image_url,
            viewers=self.viewers,
        )

    def __str__(self) -> str:
        return self.name
