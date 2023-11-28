from __future__ import annotations

from typing import NotRequired, TypedDict

from omu.extension.extension import ExtensionType
from omu.interface.keyable import Keyable
from omu.interface.model import Model


class EndpointInfoJson(TypedDict):
    extension: str
    name: str
    description: NotRequired[str] | None


class EndpointInfo(Keyable, Model[EndpointInfoJson]):
    def __init__(
        self, extension: str, name: str, description: str | None = None
    ) -> None:
        self.extension = extension
        self.name = name
        self.description = description

    @classmethod
    def from_json(cls, json: EndpointInfoJson) -> EndpointInfo:
        return EndpointInfo(**json)

    @classmethod
    def create(
        cls, extension: ExtensionType, name: str, description: str | None = None
    ) -> EndpointInfo:
        return EndpointInfo(extension.key, name, description)

    def key(self) -> str:
        return f"{self.extension}:{self.name}"

    def json(self) -> EndpointInfoJson:
        return EndpointInfoJson(
            extension=self.extension, name=self.name, description=self.description
        )

    def __str__(self) -> str:
        return f"{self.extension}:{self.name}"
