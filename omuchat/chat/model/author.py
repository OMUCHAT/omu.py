from typing import List, TypedDict

from omu.interface.keyable import Keyable
from omu.interface.model import Model

from .role import RoleJson


class AuthorJson(TypedDict):
    id: str
    name: str
    avatar_url: str
    roles: List[RoleJson]


class Author(Keyable, Model[AuthorJson]):
    def __init__(self, id: str, name: str, avatar_url: str, roles: List[RoleJson]):
        self.id = id
        self.name = name
        self.avatar_url = avatar_url
        self.roles = roles

    def key(self) -> str:
        return self.id

    def to_json(self) -> AuthorJson:
        return {
            "id": self.id,
            "name": self.name,
            "avatar_url": self.avatar_url,
            "roles": self.roles,
        }

    @classmethod
    def from_json(cls, json: AuthorJson) -> "Author":
        return cls(
            id=json["id"],
            name=json["name"],
            avatar_url=json["avatar_url"],
            roles=json["roles"],
        )
