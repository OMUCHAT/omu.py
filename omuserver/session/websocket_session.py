from __future__ import annotations

from starlette.websockets import WebSocket

from omu.event.event import EventJson
from omu.extension.server.model.app import App, AppJson
from omuserver.session.session import Session


class WebSocketSession(Session):
    def __init__(self, socket: WebSocket, app: App) -> None:
        self.socket = socket
        self._app = app

    @property
    def app(self) -> App:
        return self._app

    @classmethod
    async def create(cls, socket: WebSocket) -> WebSocketSession:
        event = EventJson.from_json_as(AppJson, await socket.receive_json())
        try:
            app = App.from_json(event.data)
        except Exception as e:
            raise ValueError(f"Received invalid app: {event}") from e
        return cls(socket, app)

    async def _receive(self) -> EventJson:
        return EventJson(**await self.socket.receive_json())

    async def start(self) -> None:
        while True:
            try:
                data = await self.socket.receive_json()
                print(data)
            except Exception as e:
                print(e)
                break
