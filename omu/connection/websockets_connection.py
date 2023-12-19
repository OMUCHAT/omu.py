import json
from typing import List

from websockets import client, exceptions

from omu.connection import Address, Connection, ConnectionListener
from omu.event import EventJson


class WebsocketsConnection(Connection):
    def __init__(self, address: Address):
        self._address = address
        self._connected = False
        self._listeners: List[ConnectionListener] = []
        self._socket = None

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

        try:
            self._socket = await client.connect(self._ws_endpoint, ping_interval=None)
            self._socket.loop.create_task(self._listen())
            self._connected = True
            for listener in self._listeners:
                await listener.on_connected()
                await listener.on_status_changed("connected")
        except exceptions.WebSocketException:
            await self.disconnect()

    async def _listen(self) -> None:
        try:
            while True:
                if not self._socket:
                    break
                try:
                    data = await self._socket.recv()
                    event = EventJson.from_json(json.loads(data))
                    for listener in self._listeners:
                        await listener.on_event(event)
                except exceptions.ConnectionClosed:
                    break
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
        data = json.dumps(
            {
                "type": event.type,
                "data": event.data,
            }
        )
        await self._socket.send(data)

    def add_listener[T: ConnectionListener](self, listener: T) -> T:
        self._listeners.append(listener)
        return listener

    def remove_listener[T: ConnectionListener](self, listener: T) -> T:
        self._listeners.remove(listener)
        return listener
