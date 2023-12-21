from __future__ import annotations

from typing import NotRequired, TypedDict

from omu.extension.extension import ExtensionType
from omu.interface import Keyable, Model


class TableInfoJson(TypedDict):
    extension: str
    name: str
    description: NotRequired[str] | None
    use_database: NotRequired[bool] | None
    cache: NotRequired[bool] | None
    cache_size: NotRequired[int] | None


class TableInfo(Keyable, Model):
    def __init__(
        self,
        extension: str,
        name: str,
        description: str | None = None,
        use_database: bool | None = None,
        cache: bool | None = None,
        cache_size: int | None = None,
    ) -> None:
        self.extension = extension
        self.name = name
        self.description = description
        self.use_database = use_database
        self.cache = cache
        self.cache_size = cache_size

    @classmethod
    def from_json(cls, json: TableInfoJson) -> TableInfo:
        return TableInfo(**json)

    @classmethod
    def create(
        cls,
        extension_type: ExtensionType,
        name: str,
        description: str | None = None,
        use_database: bool | None = None,
        cache: bool | None = None,
        cache_size: int | None = None,
    ) -> TableInfo:
        return TableInfo(
            extension=extension_type.key,
            name=name,
            description=description,
            use_database=use_database,
            cache=cache,
            cache_size=cache_size,
        )

    def key(self) -> str:
        return f"{self.extension}:{self.name}"

    def json(self) -> TableInfoJson:
        return TableInfoJson(
            extension=self.extension,
            name=self.name,
            description=self.description,
            use_database=self.use_database,
            cache=self.cache,
            cache_size=self.cache_size,
        )

    def __str__(self) -> str:
        return f"{self.extension}/{self.name}"
