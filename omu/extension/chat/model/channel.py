from datetime import datetime
from typing import TypedDict

from omu.interface.keyable import Keyable
from omu.interface.model import Model


class ChannelJson(TypedDict):
    provider_id: str
    id: str
    url: str
    name: str
    description: str
    active: bool
    icon_url: str
    created_at: int


class Channel(Keyable, Model[ChannelJson]):
    def __init__(
        self,
        provider_id: str,
        id: str,
        url: str,
        name: str,
        description: str,
        active: bool,
        icon_url: str,
        created_at: datetime,
    ) -> None:
        self.provider_id = provider_id
        self.id = id
        self.url = url
        self.name = name
        self.description = description
        self.active = active
        self.icon_url = icon_url
        self.created_at = created_at

    @classmethod
    def from_json(cls, json: ChannelJson) -> "Channel":
        return cls(
            provider_id=json["provider_id"],
            id=json["id"],
            url=json["url"],
            name=json["name"],
            description=json["description"],
            active=json["active"],
            icon_url=json["icon_url"],
            created_at=datetime.fromtimestamp(json["created_at"] / 1000),
        )

    def key(self) -> str:
        return f"{self.provider_id}:{self.url}"

    def json(self) -> ChannelJson:
        return ChannelJson(
            provider_id=self.provider_id,
            id=self.id,
            url=self.url,
            name=self.name,
            description=self.description,
            active=self.active,
            icon_url=self.icon_url,
            created_at=int(self.created_at.timestamp() * 1000),
        )
