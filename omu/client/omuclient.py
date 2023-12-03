from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, List

from loguru import logger

from omu.client import Client
from omu.connection import ConnectionListener
from omu.connection.address import Address
from omu.connection.websocket_connection import WebsocketConnection
from omu.event import EVENTS, EventJson, create_event_registry
from omu.extension import create_extension_registry
from omu.extension.endpoint.endpoint_extension import (
    EndpointExtension,
    EndpointExtensionType,
)
from omu.extension.server import ServerExtensionType
from omu.extension.server.server_extension import ServerExtension
from omu.extension.table.table_extension import TableExtension, TableExtensionType

if TYPE_CHECKING:
    from omu.client import ClientListener
    from omu.connection import Connection
    from omu.event import EventRegistry, EventType
    from omu.extension import ExtensionRegistry
    from omu.extension.server.model.app import App


class OmuClient(Client, ConnectionListener):
    def __init__(
        self,
        app: App,
        address: Address,
        connection: Connection | None = None,
        event_registry: EventRegistry | None = None,
        extension_registry: ExtensionRegistry | None = None,
    ):
        self._running = False
        self._listeners: List[ClientListener] = []
        self._app = app
        self._connection = connection or WebsocketConnection(address)
        self._connection.add_listener(self)
        self._events = event_registry or create_event_registry(self)
        self._extensions = extension_registry or create_extension_registry(self)

        self.events.register(EVENTS.Ready, EVENTS.Connect)
        self._tables = self.extensions.get(TableExtensionType)
        self._server = self.extensions.get(ServerExtensionType)
        self._endpoints = self.extensions.get(EndpointExtensionType)

        for listener in self._listeners:
            asyncio.run(listener.on_initialized())

    @property
    def connection(self) -> Connection:
        return self._connection

    @property
    def events(self) -> EventRegistry:
        return self._events

    @property
    def extensions(self) -> ExtensionRegistry:
        return self._extensions

    @property
    def endpoints(self) -> EndpointExtension:
        return self._endpoints

    @property
    def tables(self) -> TableExtension:
        return self._tables

    @property
    def server(self) -> ServerExtension:
        return self._server

    @property
    def running(self) -> bool:
        return self._running

    async def on_connected(self) -> None:
        logger.info(f"Connected to {self._connection.address}")
        await self.send(EVENTS.Connect, self._app)

    async def on_disconnected(self) -> None:
        if not self._running:
            return
        logger.warning(f"Disconnected from {self._connection.address}")
        await self._connection.connect()

    async def send[T](self, event: EventType[T, Any], data: T) -> None:
        await self._connection.send(
            EventJson(type=event.type, data=event.serializer.serialize(data))
        )

    def run(self) -> None:
        loop = asyncio.get_event_loop()
        try:
            loop.create_task(self.start())
            loop.run_forever()
        finally:
            loop.close()
            asyncio.run(self.stop())

    async def start(self) -> None:
        if self._running:
            raise RuntimeError("Already running")
        self._running = True
        for listener in self._listeners:
            await listener.on_started()
        await self._connection.connect()

    async def stop(self) -> None:
        if not self._running:
            raise RuntimeError("Not running")
        self._running = False
        await self._connection.disconnect()
        for listener in self._listeners:
            await listener.on_stopped()

    def add_listener(self, listener: ClientListener) -> None:
        self._listeners.append(listener)

    def remove_listener(self, listener: ClientListener) -> None:
        self._listeners.remove(listener)
