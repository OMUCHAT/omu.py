from typing import Any, Callable, TypedDict

from omu.client.client import Client, Coro
from omu.connection.connection import ConnectionListener
from omu.event.event import ExtensionEventType
from omu.extension.endpoint.endpoint import ClientEndpointType
from omu.extension.endpoint.model.endpoint_info import EndpointInfo
from omu.extension.extension import Extension, define_extension_type
from omu.extension.server.model.extension_info import ExtensionInfo
from omu.interface.serializable import Serializer

RegistryExtensionType = define_extension_type(
    ExtensionInfo.create("registry"),
    lambda client: RegistryExtension(client),
    lambda: [],
)


class RegistryEventData(TypedDict):
    key: str
    value: Any


RegistryUpdateEvent = ExtensionEventType[RegistryEventData, RegistryEventData](
    RegistryExtensionType, "update", Serializer.noop()
)
RegistryListenEvent = ExtensionEventType[str, str](
    RegistryExtensionType, "listen", Serializer.noop()
)
RegistryGetEndpoint = ClientEndpointType[str, Any](
    EndpointInfo.create(RegistryExtensionType, "get"), Serializer.noop()
)


class RegistryExtension(Extension, ConnectionListener):
    def __init__(self, client: Client) -> None:
        self.client = client
        self._listen_keys: set[str] = set()
        client.events.register(RegistryUpdateEvent, RegistryListenEvent)
        client.connection.add_listener(self)

    async def get[T](self, name: str, app: str | None = None) -> T:
        data: T = await self.client.endpoints.call(
            RegistryGetEndpoint, f"{app or self.client.app.key()}:{name}"
        )
        return data

    async def set[T](self, name: str, value: T, app: str | None = None) -> None:
        await self.client.send(
            RegistryUpdateEvent,
            RegistryEventData(
                key=f"{app or self.client.app.key()}:{name}", value=value
            ),
        )

    def listen[T](
        self, name: str, app: str | None = None, type: type[T] | None = None
    ) -> Callable[[Coro[[T], None]], None]:
        key = f"{app or self.client.app.key()}:{name}"

        def decorator(callback: Coro[[T], None]) -> None:
            self._listen_keys.add(key)

            async def wrapper(event: RegistryEventData) -> None:
                if event["key"] != key:
                    return
                await callback(event["value"])

            self.client.events.add_listener(RegistryUpdateEvent, wrapper)

        return decorator

    async def on_connected(self) -> None:
        for key in self._listen_keys:
            await self.client.send(RegistryListenEvent, key)
