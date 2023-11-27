import abc
from typing import Any, Callable, Protocol


class Serializer[T, D, T2, D2](abc.ABC):
    @abc.abstractmethod
    def serialize(self, item: T) -> D:
        ...

    @abc.abstractmethod
    def deserialize(self, item: D2) -> T2:
        ...


class Serializer1[T, D](Serializer[T, D, T, D]):
    ...


class _Model[T](Protocol):
    def json(self) -> T:
        ...

    def __str__(self) -> str:
        ...


def make_model_serializer[
    D, T: _Model
](deserializer: Callable[[D], T]) -> Serializer[T, D, T, D]:
    class ModelSerializer(Serializer[T, D, T, D]):
        def serialize(self, item: T) -> D:
            return item.json()

        def deserialize(self, item: D) -> T:
            return deserializer(item)

    return ModelSerializer()


def make_serializer[
    T, D
](serializer: Callable[[T], D], deserializer: Callable[[D], T]) -> Serializer[
    T, D, T, D
]:
    class SerializerImpl(Serializer[T, D, T, D]):
        def serialize(self, item: T) -> D:
            return serializer(item)

        def deserialize(self, item: D) -> T:
            return deserializer(item)

    return SerializerImpl()


def make_pass_serializer():
    class SerializerImpl(Serializer[Any, Any, Any, Any]):
        def serialize(self, item):
            return item

        def deserialize(self, item):
            return item

    return SerializerImpl()


class SerializerImpl[T, D](Serializer[T, D, T, D]):
    def __init__(self, serializer: Callable[[T], D], deserializer: Callable[[D], T]):
        self._serializer = serializer
        self._deserializer = deserializer

    def serialize(self, item: T) -> D:
        return self._serializer(item)

    def deserialize(self, data: D) -> T:
        return self._deserializer(data)
