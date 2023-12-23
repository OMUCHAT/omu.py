import asyncio
from typing import List

import aiohttp
from aiohttp import ClientSession, web

from omu.connection import Address, Connection, ConnectionListener
from omu.event import EventJson


class WebsocketsConnection(Connection):
    def __init__(self, address: Address):
        self._address = address
        self._connected = False
        self._listeners: List[ConnectionListener] = []
        self._socket: aiohttp.ClientWebSocketResponse | None = None
        self._client = ClientSession()

    @property
    def address(self) -> Address:
        return self._address

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def _ws_endpoint(self) -> str:
        protocol = "wss" if self._address.secure else "ws"
        return f"{protocol}://{self._address.host}:{self._address.port}/ws"

    async def connect(self) -> None:
        if self._socket and not self._socket.closed:
            raise RuntimeError("Already connected")

        await self.disconnect()

        self._socket = await self._client.ws_connect(self._ws_endpoint)
        asyncio.create_task(self._listen())
        self._connected = True
        for listener in self._listeners:
            await listener.on_connected()
            await listener.on_status_changed("connected")

    async def _listen(self) -> None:
        try:
            while True:
                if not self._socket:
                    break
                msg = await self._socket.receive()
                if msg.type == web.WSMsgType.CLOSE:
                    break
                elif msg.type == web.WSMsgType.ERROR:
                    break
                elif msg.type == web.WSMsgType.CLOSED:
                    break
                event = EventJson.from_json(msg.json())
                for listener in self._listeners:
                    await listener.on_event(event)
        finally:
            await self.disconnect()

    async def disconnect(self) -> None:
        if not self._socket:
            return
        if not self._socket.closed:
            try:
                await self._socket.close()
            except AttributeError:
                pass
        self._socket = None
        self._connected = False
        for listener in self._listeners:
            await listener.on_disconnected()
            await listener.on_status_changed("disconnected")

    async def send(self, event: EventJson) -> None:
        if not self._socket or self._socket.closed or not self._connected:
            raise RuntimeError("Not connected")
        await self._socket.send_json(
            {
                "type": event.type,
                "data": event.data,
            }
        )

    def add_listener[T: ConnectionListener](self, listener: T) -> T:
        self._listeners.append(listener)
        return listener

    def remove_listener[T: ConnectionListener](self, listener: T) -> T:
        self._listeners.remove(listener)
        return listener
