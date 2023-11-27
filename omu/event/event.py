from __future__ import annotations

import abc
from typing import Any

from omu.interface.serializer import Serializer


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


class EventType[T, D]():
    def __init__(self, type: str, serializer: Serializer[T, D, Any | T, Any | D]):
        self._type = type
        self._serializer = serializer

    @property
    @abc.abstractmethod
    def type(self) -> str:
        return self._type

    @property
    @abc.abstractmethod
    def serializer(self) -> Serializer[T, D, Any | T, Any | D]:
        return self._serializer
