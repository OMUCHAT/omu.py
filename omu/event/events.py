from omu.event.event import BuiltinEventType
from omu.extension.server.model.app import App, AppJson
from omu.interface import Serializer


class EVENTS:
    Connect = BuiltinEventType[App, AppJson](
        "connect",
        Serializer.model(App.from_json),
    )

    Ready = BuiltinEventType[None, None](
        "ready",
        Serializer.noop(),
    )
