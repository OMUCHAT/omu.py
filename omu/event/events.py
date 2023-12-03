from omu.event.event import BuiltinEventType
from omu.extension.server.model.app import App, AppJson
from omu.interface import Serializer

Connect = BuiltinEventType[App, AppJson](
    "Connect",
    Serializer.model(App.from_json),
)

Ready = BuiltinEventType[None, None](
    "Ready",
    Serializer.noop(),
)


class EVENTS:
    Connect = Connect
    Ready = Ready
