from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, List

from loguru import logger

from omuchat.client import Client
from omuchat.connection import ConnectionListener
from omuchat.endpoint import Endpoint
from omuchat.endpoint.http_endpoint import HttpEndpoint
from omuchat.event import EVENTS, EventJson, create_event_registry
from omuchat.extension import create_extension_registry
from omuchat.extension.chat.chat_extension import ChatExtensionType
from omuchat.extension.server import ServerExtensionType
from omuchat.extension.table.table_extension import TableExtensionType

if TYPE_CHECKING:
    from omuchat.client import ClientListener
    from omuchat.connection import Connection
    from omuchat.event import EventRegistry, EventType
    from omuchat.extension import ExtensionRegistry
    from omuchat.extension.server.model.app import App


class OmuClient(Client, ConnectionListener):
    def __init__(
        self,
        app: App,
        connection: Connection,
        endpoint: Endpoint | None = None,
        event_registry: EventRegistry | None = None,
        extension_registry: ExtensionRegistry | None = None,
    ):
        self._running = False
        self._listeners: List[ClientListener] = []
        self._app = app
        self._connection = connection
        self._endpoint = endpoint or HttpEndpoint(connection.address)
        self._events = event_registry or create_event_registry(self)
        self._extensions = extension_registry or create_extension_registry(self)

        self.events.register(EVENTS.Ready, EVENTS.Connect)
        self.extensions.register(
            TableExtensionType, ServerExtensionType, ChatExtensionType
        )

        connection.add_listener(self)
        for listener in self._listeners:
            asyncio.run(listener.on_initialized())

    @property
    def connection(self) -> Connection:
        return self._connection

    @property
    def endpoint(self) -> Endpoint:
        return self._endpoint

    @property
    def events(self) -> EventRegistry:
        return self._events

    @property
    def extensions(self) -> ExtensionRegistry:
        return self._extensions

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

    async def start(self) -> None:
        if self._running:
            raise RuntimeError("Already running")
        self._running = True
        await self._connection.connect()
        for listener in self._listeners:
            await listener.on_started()

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
