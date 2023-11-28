from __future__ import annotations

import abc
from typing import AsyncIterator, Dict

from omu.extension.table.model.table_info import TableInfo
from omu.interface.keyable import Keyable
from omu.interface.serializable import Serializable


class Table[T: Keyable](abc.ABC):
    @property
    @abc.abstractmethod
    def cache(self) -> Dict[str, T]:
        ...

    @abc.abstractmethod
    async def get(self, key: str) -> T | None:
        ...

    @abc.abstractmethod
    async def add(self, *items: T) -> None:
        ...

    @abc.abstractmethod
    async def set(self, *items: T) -> None:
        ...

    @abc.abstractmethod
    async def remove(self, *items: T) -> None:
        ...

    @abc.abstractmethod
    async def clear(self) -> None:
        ...

    @abc.abstractmethod
    async def fetch(self, limit: int = 100, cursor: str | None = None) -> None:
        ...

    @abc.abstractmethod
    async def iterator(self) -> AsyncIterator[T]:
        ...

    @abc.abstractmethod
    async def size(self) -> int:
        ...

    @abc.abstractmethod
    def add_listener(self, listener: TableListener[T]) -> None:
        ...

    @abc.abstractmethod
    def remove_listener(self, listener: TableListener[T]) -> None:
        ...


class TableListener[T: Keyable]:
    async def on_add(self, items: Dict[str, T]) -> None:
        ...

    async def on_set(self, items: Dict[str, T]) -> None:
        ...

    async def on_remove(self, items: Dict[str, T]) -> None:
        ...

    async def on_clear(self) -> None:
        ...

    async def on_cache_update(self, cache: Dict[str, T]) -> None:
        ...


class TableType[T: Keyable, D](abc.ABC):
    @property
    @abc.abstractmethod
    def info(self) -> TableInfo:
        ...

    @property
    @abc.abstractmethod
    def serializer(self) -> Serializable[T, D]:
        ...


class ModelTableType[T: Keyable, D](TableType[T, D]):
    def __init__(self, info: TableInfo, serializer: Serializable[T, D]):
        self._info = info
        self._serializer = serializer

    @property
    def info(self) -> TableInfo:
        return self._info

    @property
    def serializer(self) -> Serializable[T, D]:
        return self._serializer
