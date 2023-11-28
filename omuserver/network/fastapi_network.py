import threading
from typing import Any, Awaitable, Callable, Dict, List

from fastapi import FastAPI
from fastapi.websockets import WebSocket
from starlette.middleware.cors import CORSMiddleware
from uvicorn import run

from omu.endpoint.endpoint import EndpointType
from omuserver.network.network import Network, NetworkListener
from omuserver.server import Server, ServerListener
from omuserver.session.session import Session, SessionListener
from omuserver.session.websocket_session import WebSocketSession


class FastAPINetwork(Network, ServerListener, SessionListener):
    def __init__(self, server: Server, app: FastAPI) -> None:
        self._server = server
        self._app = app
        self._listeners: List[NetworkListener] = []
        self._endpoints: Dict[str, Callable[[Session, Any], Awaitable[Any]]] = {}
        self._sessions: Dict[str, WebSocketSession] = {}
        self._app.websocket_route("/api/v1/ws")(self._websocket_handler)
        server.add_listener(self)

    async def bind_endpoint[
        ReqData, ResData
    ](
        self,
        type: EndpointType[Any, Any, ReqData, ResData],
        handler: Callable[[Session, ReqData], Awaitable[ResData]],
    ) -> None:
        if type.key in self._endpoints:
            raise ValueError(f"Endpoint {type.key} already bound")
        self._endpoints[type.key] = handler
        self._app.post(f"/api/v1/{type.key}")(self._endpoint_handler(type))

    def _endpoint_handler(
        self, type: EndpointType[Any, Any, Any, Any]
    ) -> Callable[[Any], Awaitable[Any]]:
        async def _handler(data: Any) -> Any:
            session = self._sessions[data["session"]]
            if session is None:
                raise ValueError(f"Session {data['session']} not found")
            handler = self._endpoints[type.key]
            if handler is None:
                raise ValueError(f"Endpoint {type.key} not bound")
            return await handler(session, data["data"])

        return _handler

    async def _websocket_handler(self, websocket: WebSocket) -> None:
        await websocket.accept()
        session = await WebSocketSession.create(websocket)
        if session.app.key() in self._sessions:
            raise ValueError(f"Session {session.app.key()} already exists")
        self._sessions[session.app.key()] = session
        session.add_listener(self)
        for listener in self._listeners:
            await listener.on_connect(session)
        await session.start()

    async def on_disconnected(self, session: Session) -> None:
        if session.app.key() in self._sessions:
            del self._sessions[session.app.key()]
        for listener in self._listeners:
            await listener.on_disconnected(session)

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
