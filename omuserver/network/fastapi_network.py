import threading

from fastapi import FastAPI
from fastapi.websockets import WebSocket
from starlette.middleware.cors import CORSMiddleware
from uvicorn import run

from omuserver.network.network import Network, NetworkListener
from omuserver.server import Server, ServerListener
from omuserver.session.websocket_session import WebSocketSession


class FastAPINetwork(Network, ServerListener):
    def __init__(self, server: Server, app: FastAPI) -> None:
        self._server = server
        self._app = app
        self._listeners: list[NetworkListener] = []
        self._app.websocket_route("/api/v1/ws")(self._websocket_handler)
        server.add_listener(self)

    async def _websocket_handler(self, websocket: WebSocket) -> None:
        await websocket.accept()
        session = await WebSocketSession.create(websocket)
        for listener in self._listeners:
            await listener.on_connect(session)
        await session.start()

    async def start(self) -> None:
        address = self._server.address

        def _thread() -> None:
            self._app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
            run(self._app, host=address.host, port=address.port, loop="asyncio")

        thread = threading.Thread(target=_thread, daemon=True, name="FastAPI")
        thread.start()

    def add_listener(self, listener: NetworkListener) -> None:
        self._listeners.append(listener)

    def remove_listener(self, listener: NetworkListener) -> None:
        self._listeners.remove(listener)
