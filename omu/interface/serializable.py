from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from omu.interface import Model


class Serializable[T, D](abc.ABC):
    @abc.abstractmethod
    def serialize(self, item: T) -> D:
        ...

    @abc.abstractmethod
    def deserialize(self, item: D) -> T:
        ...


class Serializer[T, D](Serializable[T, D]):
    def __init__(self, serialize: Callable[[T], D], deserialize: Callable[[D], T]):
        self._serialize = serialize
        self._deserialize = deserialize

    def serialize(self, item: T) -> D:
        return self._serialize(item)

    def deserialize(self, item: D) -> T:
        return self._deserialize(item)

    @classmethod
    def noop(cls) -> Serializable[T, T]:
        return Serializer(lambda item: item, lambda item: item)

    @classmethod
    def model[M: Model, _D](cls, model: Callable[[_D], M]) -> Serializable[M, _D]:
        return Serializer(lambda item: item.json(), model)

    @classmethod
    def array[_T, _D](
        cls, serializer: Serializable[_T, _D]
    ) -> Serializable[list[_T], list[_D]]:
        return Serializer(
            lambda items: [serializer.serialize(item) for item in items],
            lambda items: [serializer.deserialize(item) for item in items],
        )

    @classmethod
    def map[_T, _D](
        cls, serializer: Serializable[_T, _D]
    ) -> Serializable[dict[str, _T], dict[str, _D]]:
        return Serializer(
            lambda items: {
                key: serializer.serialize(value) for key, value in items.items()
            },
            lambda items: {
                key: serializer.deserialize(value) for key, value in items.items()
            },
        )
