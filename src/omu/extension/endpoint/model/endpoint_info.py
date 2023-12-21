from __future__ import annotations

from typing import NotRequired, TypedDict

from omu.extension.extension import ExtensionType
from omu.interface import Keyable, Model


class EndpointInfoJson(TypedDict):
    app: str
    name: str
    description: NotRequired[str] | None


class EndpointInfo(Keyable, Model[EndpointInfoJson]):
    def __init__(
        self,
        app: str,
        name: str,
        description: str | None = None,
    ) -> None:
        self.app = app
        self.name = name
        self.description = description

    @classmethod
    def from_json(cls, json: EndpointInfoJson) -> EndpointInfo:
        return EndpointInfo(**json)

    def json(self) -> EndpointInfoJson:
        return EndpointInfoJson(
            app=self.app,
            name=self.name,
            description=self.description,
        )

    @classmethod
    def create(
        cls,
        extension: ExtensionType,
        name: str,
        description: str | None = None,
    ) -> EndpointInfo:
        return EndpointInfo(
            app=extension.key,
            name=name,
            description=description,
        )

    def key(self) -> str:
        return f"{self.app}:{self.name}"

    def __str__(self) -> str:
        return f"EndpointInfo({self.key()})"
