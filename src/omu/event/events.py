from omu.event.event import JsonEventType, SerializeEventType
from omu.extension.server.model.app import App
from omu.interface import Serializer


class EVENTS:
    Connect = SerializeEventType(
        "",
        "connect",
        Serializer.model(App),
    )

    Ready = JsonEventType[None](
        "",
        "ready",
        Serializer.noop(),
    )
