from __future__ import annotations

import abc
from pathlib import Path
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from omu.connection import Address
    from omuserver.event.event_registry import EventRegistry
    from omuserver.extension.extension import Extension
    from omuserver.network.network import Network


class ServerListener:
    async def on_initialized(self) -> None:
        ...

    async def on_started(self) -> None:
        ...

    async def on_stopped(self) -> None:
        ...


class Server(abc.ABC):
    @property
    @abc.abstractmethod
    def address(self) -> Address:
        ...

    @property
    @abc.abstractmethod
    def network(self) -> Network:
        ...

    @property
    @abc.abstractmethod
    def events(self) -> EventRegistry:
        ...

    @property
    @abc.abstractmethod
    def extensions(self) -> Dict[str, Extension]:
        ...

    @property
    @abc.abstractmethod
    def data_path(self) -> Path:
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
    def add_listener[T: ServerListener](self, listener: T) -> T:
        ...

    @abc.abstractmethod
    def remove_listener[T: ServerListener](self, listener: T) -> T:
        ...
