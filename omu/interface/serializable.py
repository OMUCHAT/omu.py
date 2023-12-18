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
        return NoopSerializer()

    @classmethod
    def model[M: Model, _D](cls, model: Callable[[_D], M]) -> Serializable[M, _D]:
        return ModelSerializer(model)

    @classmethod
    def array[_T, _D](
        cls, serializer: Serializable[_T, _D]
    ) -> Serializable[list[_T], list[_D]]:
        return ArraySerializer(serializer)

    @classmethod
    def map[_T, _D](
        cls, serializer: Serializable[_T, _D]
    ) -> Serializable[dict[str, _T], dict[str, _D]]:
        return MapSerializer(serializer)


class NoopSerializer[T](Serializable[T, T]):
    def serialize(self, item: T) -> T:
        return item

    def deserialize(self, item: T) -> T:
        return item

    def __repr__(self) -> str:
        return "NoopSerializer()"


class ModelSerializer[M: Model, _D](Serializable[M, _D]):
    def __init__(self, model: Callable[[_D], M]):
        self._model = model

    def serialize(self, item: M) -> _D:
        return item.json()

    def deserialize(self, item: _D) -> M:
        return self._model(item)

    def __repr__(self) -> str:
        return f"ModelSerializer({self._model})"


class ArraySerializer[_T, _D](Serializable[list[_T], list[_D]]):
    def __init__(self, serializer: Serializable[_T, _D]):
        self._serializer = serializer

    def serialize(self, items: list[_T]) -> list[_D]:
        return [self._serializer.serialize(item) for item in items]

    def deserialize(self, items: list[_D]) -> list[_T]:
        return [self._serializer.deserialize(item) for item in items]

    def __repr__(self) -> str:
        return f"ArraySerializer({self._serializer})"


class MapSerializer[_T, _D](Serializable[dict[str, _T], dict[str, _D]]):
    def __init__(self, serializer: Serializable[_T, _D]):
        self._serializer = serializer

    def serialize(self, items: dict[str, _T]) -> dict[str, _D]:
        return {key: self._serializer.serialize(value) for key, value in items.items()}

    def deserialize(self, items: dict[str, _D]) -> dict[str, _T]:
        return {
            key: self._serializer.deserialize(value) for key, value in items.items()
        }

    def __repr__(self) -> str:
        return f"MapSerializer({self._serializer})"
