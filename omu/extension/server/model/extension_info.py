from __future__ import annotations

from typing import NotRequired, TypedDict

from omu.interface.keyable import Keyable
from omu.interface.model import Model


class ExtensionInfoJson(TypedDict):
    name: str
    description: NotRequired[str] | None


class ExtensionInfo(Keyable, Model[ExtensionInfoJson]):
    def __init__(self, name: str, description: str | None = None) -> None:
        self.name = name
        self.description = description

    @classmethod
    def from_json(cls, json: ExtensionInfoJson) -> ExtensionInfo:
        return ExtensionInfo(**json)

    @classmethod
    def create(cls, name: str, description: str | None = None) -> ExtensionInfo:
        return ExtensionInfo(name, description)

    def key(self) -> str:
        return self.name

    def json(self) -> ExtensionInfoJson:
        return ExtensionInfoJson(name=self.name, description=self.description)

    def __str__(self) -> str:
        return self.name
