from __future__ import annotations

import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omu.extension.server import App


class Session(abc.ABC):
    @property
    @abc.abstractmethod
    def app(self) -> App:
        ...

    @abc.abstractmethod
    def add_listener(self, listener: SessionListener) -> None:
        ...

    @abc.abstractmethod
    def remove_listener(self, listener: SessionListener) -> None:
        ...


class SessionListener:
    async def on_message(self, message: str) -> None:
        ...

    async def on_error(self, error: Exception) -> None:
        ...
