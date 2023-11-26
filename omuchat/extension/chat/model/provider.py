from typing import TypedDict

from omuchat.interface.keyable import Keyable
from omuchat.interface.model import Model


class ProviderJson(TypedDict):
    id: str
    url: str
    name: str
    image_url: str | None
    description: str
    regex: str


class Provider(Keyable, Model[ProviderJson]):
    def __init__(
        self,
        id: str,
        url: str,
        name: str,
        image_url: str | None,
        description: str,
        regex: str,
    ) -> None:
        self.id = id
        self.url = url
        self.name = name
        self.image_url = image_url
        self.description = description
        self.regex = regex

    @classmethod
    def from_json(cls, json: ProviderJson) -> "Provider":
        return cls(
            id=json["id"],
            url=json["url"],
            name=json["name"],
            image_url=json["image_url"],
            description=json["description"],
            regex=json["regex"],
        )

    def key(self) -> str:
        return self.id

    def json(self) -> ProviderJson:
        return ProviderJson(
            id=self.id,
            url=self.url,
            name=self.name,
            image_url=self.image_url,
            description=self.description,
            regex=self.regex,
        )

    def __str__(self) -> str:
        return self.name
