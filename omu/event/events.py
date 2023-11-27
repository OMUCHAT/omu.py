from omu.event import EventType
from omu.extension.server.model.app import App, AppJson
from omu.interface.serializer import SerializerImpl

Connect = EventType[App, AppJson](
    "Connect",
    SerializerImpl[App, AppJson](
        serializer=lambda app: app.json(),
        deserializer=lambda data: App.from_json(data),
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
