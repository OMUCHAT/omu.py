from __future__ import annotations

import abc
import asyncio
from typing import TYPE_CHECKING, Any, Coroutine

if TYPE_CHECKING:
    from omu.connection import Connection
    from omu.event import EventType
    from omu.event.event_registry import EventRegistry
    from omu.extension import ExtensionRegistry
    from omu.extension.endpoint.endpoint_extension import EndpointExtension
    from omu.extension.server.server_extension import ServerExtension
    from omu.extension.table.table_extension import TableExtension


class ClientListener:
    async def on_initialized(self) -> None:
        ...

    async def on_started(self) -> None:
        ...

    async def on_stopped(self) -> None:
        ...


type Coro = Coroutine[Any, Any, None]


class Client(abc.ABC):
    @property
    @abc.abstractmethod
    def loop(self) -> asyncio.AbstractEventLoop:
        ...

    @property
    @abc.abstractmethod
    def connection(self) -> Connection:
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
    def endpoints(self) -> EndpointExtension:
        ...

    @property
    @abc.abstractmethod
    def tables(self) -> TableExtension:
        ...

    @property
    @abc.abstractmethod
    def server(self) -> ServerExtension:
        ...

    @property
    @abc.abstractmethod
    def running(self) -> bool:
        ...

    @abc.abstractmethod
    def run(self) -> None:
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
