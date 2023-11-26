from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from omuchat.connection import Connection
    from omuchat.endpoint import Endpoint
    from omuchat.event import EventType
    from omuchat.event.event_registry import EventRegistry
    from omuchat.extension import ExtensionRegistry


class ClientListener:
    async def on_initialized(self) -> None:
        ...

    async def on_started(self) -> None:
        ...

    async def on_stopped(self) -> None:
        ...


class Client(abc.ABC):
    @property
    @abc.abstractmethod
    def connection(self) -> Connection:
        ...

    @property
    @abc.abstractmethod
    def endpoint(self) -> Endpoint:
        ...

    @property
    @abc.abstractmethod
    def events(self) -> EventRegistry:
        ...

    @property
    @abc.abstractmethod
    def extensions(self) -> ExtensionRegistry:
        ...

    @property
    @abc.abstractmethod
    def running(self) -> bool:
        ...

    @abc.abstractmethod
    async def start(self) -> None:
        ...

    @abc.abstractmethod
    async def stop(self) -> None:
        ...

    @abc.abstractmethod
    async def send[T](self, type: EventType[T, Any], data: T) -> None:
        ...

    @abc.abstractmethod
    def add_listener[T: ClientListener](self, listener: T) -> T:
        ...

    @abc.abstractmethod
    def remove_listener[T: ClientListener](self, listener: T) -> T:
        ...
