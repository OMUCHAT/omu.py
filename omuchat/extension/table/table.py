from __future__ import annotations

import abc
from typing import AsyncIterator, Callable, Dict, Protocol, TypeVar

from omuchat.extension import ExtensionType
from omuchat.interface.keyable import Keyable
from omuchat.interface.serializer import Serializer, make_model_serializer


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
    async def add_listener(self, listener: TableListener[T]) -> None:
        ...

    @abc.abstractmethod
    async def remove_listener(self, listener: TableListener[T]) -> None:
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


class _Keyable(Protocol):
    def key(self) -> str:
        ...


class TableType[T: _Keyable, D](abc.ABC):
    @property
    @abc.abstractmethod
    def key(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def serializer(self) -> Serializer[T, D, T | None, D]:
        ...


def define_table_type[
    T: Keyable, D
](
    extension_type: ExtensionType,
    key: str,
    serializer: Serializer[T, D, T | None, D],
) -> TableType[T, D]:
    class _TableType(TableType[T, D]):
        @property
        def key(self) -> str:
            return f"{extension_type.key}:{key}"

        @property
        def serializer(self) -> Serializer[T, D, T | None, D]:
            return serializer

    return _TableType()


class KeyableModel[T](Protocol):
    def key(self) -> str:
        ...

    def json(self) -> T:
        ...

    def __str__(self) -> str:
        ...


T = TypeVar("T", bound=KeyableModel)
D = TypeVar("D")


def define_table_type_model(
    extension_type: ExtensionType,
    key: str,
    _t: type[T],
    _d: type[D],
    deserialize: Callable[[D], T],
) -> TableType[T, D]:
    class _TableType(TableType):
        @property
        def key(self) -> str:
            return f"{extension_type.key}:{key}"

        @property
        def serializer(self) -> Serializer[T, D, T | None, D]:
            return make_model_serializer(deserialize)

    return _TableType()
