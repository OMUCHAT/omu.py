from __future__ import annotations

import abc
from typing import Callable

from omu.interface.model import Model


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

    @classmethod
    def noop(cls) -> Serializable[T, T]:
        return Serializer(lambda item: item, lambda item: item)

    @classmethod
    def model[M: Model, _D](cls, model: Callable[[_D], M]) -> Serializable[M, _D]:
        return Serializer(lambda item: item.json(), model)

    def serialize(self, item: T) -> D:
        return self._serialize(item)

    def deserialize(self, item: D) -> T:
        return self._deserialize(item)
