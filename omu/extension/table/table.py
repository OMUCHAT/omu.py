from __future__ import annotations

import abc
from typing import AsyncGenerator, Callable, Coroutine, Dict

from omu.extension.table.model.table_info import TableInfo
from omu.interface import Keyable, Serializable

type AsyncCallback[**P] = Callable[P, Coroutine]


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
    async def iter(self) -> AsyncGenerator[T, None]:
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

    @abc.abstractmethod
    def listen(self, listener: AsyncCallback[Dict[str, T]] | None = None) -> None:
        ...


class TableListener[T: Keyable]:
    async def on_add(self, items: Dict[str, T]) -> None:
        ...

    async def on_update(self, items: Dict[str, T]) -> None:
        ...

    async def on_remove(self, items: Dict[str, T]) -> None:
        ...

    async def on_clear(self) -> None:
        ...

    async def on_cache_update(self, cache: Dict[str, T]) -> None:
        ...


class CallbackTableListener[T: Keyable](TableListener[T]):
    def __init__(
        self,
        on_add: AsyncCallback[Dict[str, T]] | None = None,
        on_update: AsyncCallback[Dict[str, T]] | None = None,
        on_remove: AsyncCallback[Dict[str, T]] | None = None,
        on_clear: AsyncCallback[[]] | None = None,
        on_cache_update: AsyncCallback[Dict[str, T]] | None = None,
    ):
        self._on_add = on_add
        self._on_update = on_update
        self._on_remove = on_remove
        self._on_clear = on_clear
        self._on_cache_update = on_cache_update

    async def on_add(self, items: Dict[str, T]) -> None:
        if self._on_add:
            await self._on_add(items)

    async def on_update(self, items: Dict[str, T]) -> None:
        if self._on_update:
            await self._on_update(items)

    async def on_remove(self, items: Dict[str, T]) -> None:
        if self._on_remove:
            await self._on_remove(items)

    async def on_clear(self) -> None:
        if self._on_clear:
            await self._on_clear()

    async def on_cache_update(self, cache: Dict[str, T]) -> None:
        if self._on_cache_update:
            await self._on_cache_update(cache)


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
