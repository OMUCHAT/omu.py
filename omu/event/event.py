from __future__ import annotations

import abc

from omu.extension.extension import ExtensionType
from omu.interface.serializable import Serializable


class EventJson[T]:
    def __init__(self, type: str, data: T):
        self.type = type
        self.data = data

    @classmethod
    def from_json(cls, json: dict) -> EventJson[T]:
        if "type" not in json:
            raise ValueError("Missing type field in event json")
        if "data" not in json:
            raise ValueError("Missing data field in event json")
        return cls(**json)

    @classmethod
    def from_json_as[_T](cls, _t: type[_T], json: dict) -> EventJson[_T]:
        if "type" not in json:
            raise ValueError("Missing type field in event json")
        if "data" not in json:
            raise ValueError("Missing data field in event json")
        return cls(**json)  # type: ignore

    def __str__(self) -> str:
        return f"{self.type}:{self.data}"

    def __repr__(self) -> str:
        return f"{self.type}:{self.data}"


class EventType[T, D](abc.ABC):
    @property
    @abc.abstractmethod
    def type(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def serializer(self) -> Serializable[T, D]:
        ...

    def __str__(self) -> str:
        return self.type

    def __repr__(self) -> str:
        return self.type


class BuiltinEventType[T, D](EventType[T, D]):
    def __init__(self, type: str, serializer: Serializable[T, D]):
        self._type = type
        self._serializer = serializer

    @property
    def type(self) -> str:
        return self._type

    @property
    def serializer(self) -> Serializable[T, D]:
        return self._serializer


class ExtensionEventType[T, D](EventType[T, D]):
    def __init__(
        self, extension_type: ExtensionType, type: str, serializer: Serializable[T, D]
    ):
        self._extension_type = extension_type
        self._type = type
        self._serializer = serializer

    @property
    def type(self) -> str:
        return f"{self._extension_type.key}:{self._type}"

    @property
    def serializer(self) -> Serializable[T, D]:
        return self._serializer
