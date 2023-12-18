from __future__ import annotations

from asyncio import Future
from typing import Any, Dict, TypedDict

from omu.client import Client
from omu.event.event import ExtensionEventType
from omu.extension.endpoint.endpoint import EndpointType
from omu.extension.endpoint.model.endpoint_info import EndpointInfo, EndpointInfoJson
from omu.extension.extension import Extension, define_extension_type
from omu.extension.server.model.extension_info import ExtensionInfo
from omu.extension.table.model.table_info import TableInfo
from omu.extension.table.table import ModelTableType
from omu.interface import Serializer

EndpointExtensionType = define_extension_type(
    ExtensionInfo.create("endpoint"),
    lambda client: EndpointExtension(client),
    lambda: [],
)


class EndpointExtension(Extension):
    def __init__(self, client: Client) -> None:
        self.client = client
        self.endpoints: Dict[str, EndpointType] = {}
        self.promises: Dict[int, Future] = {}
        self.key = 0
        client.events.register(
            EndpointCallEvent, EndpointReceiveEvent, EndpointErrorEvent
        )
        client.events.add_listener(EndpointReceiveEvent, self._on_receive)
        client.events.add_listener(EndpointErrorEvent, self._on_error)

    async def _on_receive(self, data: EndpointDataReq) -> None:
        if data["key"] not in self.promises:
            return
        future = self.promises[data["key"]]
        future.set_result(data["data"])
        self.promises.pop(data["key"])

    async def _on_error(self, data: EndpointError) -> None:
        if data["key"] not in self.promises:
            return
        future = self.promises[data["key"]]
        future.set_exception(Exception(data["error"]))

    def register(self, type: EndpointType) -> None:
        if type.info.key() in self.endpoints:
            raise Exception(f"Endpoint for key {type.info.key()} already registered")
        self.endpoints[type.info.key()] = type

    async def execute[Req, Res, ReqData, ResData](
        self, endpoint: EndpointType[Req, Res, ReqData, ResData], data: Req
    ) -> Future[ResData]:
        json = endpoint.request_serializer.serialize(data)
        future = await self._call(endpoint, json)
        return future

    async def call[Req, Res, ReqData, ResData](
        self, endpoint: EndpointType[Req, Res, ReqData, ResData], data: Req
    ) -> Res:
        try:
            future = await self.execute(endpoint, data)
            return endpoint.response_serializer.deserialize(await future)
        except Exception as e:
            raise Exception(f"Error calling endpoint {endpoint.info.key()}") from e

    async def _call[ReqData, ResData](
        self, endpoint: EndpointType[Any, Any, ReqData, ResData], data: ReqData
    ) -> Future[ResData]:
        self.key += 1
        future = Future()
        self.promises[self.key] = future
        await self.client.send(
            EndpointCallEvent,
            EndpointDataReq(type=endpoint.info.key(), key=self.key, data=data),
        )
        return future


class EndpointReq(TypedDict):
    type: str
    key: int


class EndpointDataReq(TypedDict):
    type: str
    key: int
    data: Any


class EndpointError(TypedDict):
    type: str
    key: int
    error: str


EndpointRegisterEvent = ExtensionEventType[EndpointInfo, EndpointInfoJson](
    EndpointExtensionType, "register", Serializer.model(EndpointInfo.from_json)
)


EndpointCallEvent = ExtensionEventType[EndpointDataReq, EndpointDataReq](
    EndpointExtensionType, "call", Serializer.noop()
)
EndpointReceiveEvent = ExtensionEventType[EndpointDataReq, EndpointDataReq](
    EndpointExtensionType, "receive", Serializer.noop()
)
EndpointErrorEvent = ExtensionEventType[EndpointError, EndpointError](
    EndpointExtensionType, "error", Serializer.noop()
)
EndpointsTableType = ModelTableType[EndpointInfo, EndpointInfoJson](
    TableInfo.create(EndpointExtensionType, "endpoints"),
    Serializer.model(lambda data: EndpointInfo.from_json(data)),
)
