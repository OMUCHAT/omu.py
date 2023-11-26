from typing import NotRequired, TypedDict

from omuchat.interface.keyable import Keyable
from omuchat.interface.model import Model


class RoleJson(TypedDict):
    id: str
    name: str
    icon_url: str
    is_owner: bool
    is_moderator: bool
    color: NotRequired[str] | None


class Role(Keyable, Model[RoleJson]):
    def __init__(
        self,
        id: str,
        name: str,
        icon_url: str,
        is_owner: bool,
        is_moderator: bool,
        color: str | None = None,
    ) -> None:
        self.id = id
        self.name = name
        self.icon_url = icon_url
        self.is_owner = is_owner
        self.is_moderator = is_moderator
        self.color = color

    def key(self) -> str:
        return self.id

    def json(self) -> RoleJson:
        return {
            "id": self.id,
            "name": self.name,
            "icon_url": self.icon_url,
            "is_owner": self.is_owner,
            "is_moderator": self.is_moderator,
            "color": self.color,
        }

    @classmethod
    def from_json(cls, json: RoleJson) -> "Role":
        return cls(
            id=json["id"],
            name=json["name"],
            icon_url=json["icon_url"],
            is_owner=json["is_owner"],
            is_moderator=json["is_moderator"],
            color=json["color"],
        )

    def __str__(self) -> str:
        return self.name
