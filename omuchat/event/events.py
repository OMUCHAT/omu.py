from typing import TypedDict

from omuchat.event import EventType
from omuchat.extension.server.model.app import App, AppJson
from omuchat.interface.serializer import SerializerImpl


class _Connect(TypedDict):
    app: AppJson


Connect = EventType[App, _Connect](
    "Connect",
    SerializerImpl[App, _Connect](
        serializer=lambda app: _Connect(app=app.json()),
        deserializer=lambda data: App.from_json(data["app"]),
    ),
)

Ready = EventType[None, None](
    "Ready",
    SerializerImpl[None, None](
        serializer=lambda _: None,
        deserializer=lambda _: None,
    ),
)


class EVENTS:
    Connect = Connect
    Ready = Ready
