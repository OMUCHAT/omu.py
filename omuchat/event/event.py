import abc
from typing import Any

from pydantic import BaseModel

from omuchat.interface.serializer import Serializer


class EventJson[T](BaseModel):
    type: str
    data: T


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
