from typing import Dict, Optional

from fastapi import FastAPI

from omu.connection.address import Address
from omuserver.extension.extension import ServerExtension
from omuserver.network import FastAPINetwork, Network

from .server import Server, ServerListener


class FastApiServer(Server):
    def __init__(
        self,
        address: Address,
        app: Optional[FastAPI] = None,
        network: Optional[Network] = None,
    ) -> None:
        self._address = address
        self._app = app or FastAPI()
        self._listeners = []
        self._network = network or FastAPINetwork(self, self._app)
        self._extensions: Dict[str, ServerExtension] = {}
        self._running = False

    @property
    def address(self) -> Address:
        return self._address

    @property
    def network(self) -> Network:
        return self._network

    @property
    def running(self) -> bool:
        return self._running

    async def start(self) -> None:
        self._running = True
        await self._network.start()
        self._running = False

    async def stop(self) -> None:
        self._running = False

    def add_listener(self, listener: ServerListener) -> None:
        self._listeners.append(listener)

    def remove_listener(self, listener: ServerListener) -> None:
        self._listeners.remove(listener)
