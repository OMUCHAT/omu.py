from __future__ import annotations

from typing import NotRequired, TypedDict

from omu.extension.extension import ExtensionType
from omu.interface.keyable import Keyable
from omu.interface.model import Model


class TableInfoJson(TypedDict):
    extension: str
    name: str
    description: NotRequired[str] | None
    use_database: NotRequired[bool] | None


class TableInfo(Keyable, Model):
    def __init__(
        self,
        extension: str,
        name: str,
        description: str | None = None,
        use_database: bool | None = None,
    ) -> None:
        self.extension = extension
        self.name = name
        self.description = description
        self.use_database = use_database

    @classmethod
    def from_json(cls, json: TableInfoJson) -> TableInfo:
        return TableInfo(**json)

    @classmethod
    def create(cls, extension_type: ExtensionType, name: str) -> TableInfo:
        return TableInfo(extension_type.key, name)

    def key(self) -> str:
        return f"{self.extension}:{self.name}"

    def json(self) -> TableInfoJson:
        return TableInfoJson(
            extension=self.extension,
            name=self.name,
            description=self.description,
            use_database=self.use_database,
        )

    def __str__(self) -> str:
        return f"{self.extension}/{self.name}"
