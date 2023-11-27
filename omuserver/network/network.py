from __future__ import annotations

import abc

from omuserver.session.session import Session


class Network(abc.ABC):
    @abc.abstractmethod
    async def start(self) -> None:
        ...

    @abc.abstractmethod
    def add_listener(self, listener: NetworkListener) -> None:
        ...

    @abc.abstractmethod
    def remove_listener(self, listener: NetworkListener) -> None:
        ...


class NetworkListener:
    async def on_connect(self, session: Session) -> None:
        ...
