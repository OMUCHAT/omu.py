from __future__ import annotations

from typing import NotRequired, TypedDict

from omu.extension.extension import ExtensionType
from omu.interface import Keyable, Model


class EndpointInfoJson(TypedDict):
    extension: str
    name: str
    description: NotRequired[str] | None
    cache: NotRequired[bool] | None
    cache_size: NotRequired[int] | None


class EndpointInfo(Keyable, Model[EndpointInfoJson]):
    def __init__(
        self,
        extension: str,
        name: str,
        description: str | None = None,
        cache: bool | None = None,
        cache_size: int | None = None,
    ) -> None:
        self.extension = extension
        self.name = name
        self.description = description
        self.cache = cache
        self.cache_size = cache_size

    @classmethod
    def from_json(cls, json: EndpointInfoJson) -> EndpointInfo:
        return EndpointInfo(**json)

    def json(self) -> EndpointInfoJson:
        return {
            "extension": self.extension,
            "name": self.name,
            "description": self.description,
            "cache": self.cache,
            "cache_size": self.cache_size,
        }

    @classmethod
    def create(
        cls,
        extension: ExtensionType,
        name: str,
        description: str | None = None,
        cache: bool | None = None,
        cache_size: int | None = None,
    ) -> EndpointInfo:
        return EndpointInfo(
            extension=extension.key,
            name=name,
            description=description,
            cache=cache,
            cache_size=cache_size,
        )

    def key(self) -> str:
        return f"{self.extension}:{self.name}"

    def __str__(self) -> str:
        return f"EndpointInfo({self.key()})"
