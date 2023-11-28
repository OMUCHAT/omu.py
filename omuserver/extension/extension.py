from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Callable, List

from omu.endpoint import EndpointType
from omu.event import EventType
from omuserver.server import Server

if TYPE_CHECKING:
    from omu.interface.serializer import Serializable


class ServerExtension(abc.ABC):
    pass


class ExtensionType[T: ServerExtension]():
    def __init__(
        self, key: str, create: Callable[[Server], T], dependencies: List[ExtensionType]
    ):
        self._key = key
        self._create = create
        self._dependencies = dependencies

    @property
    def key(self) -> str:
        return self._key

    def create(self, server: Server) -> T:
        return self._create(server)

    def define_event_type[
        _T, _D
    ](
        self, _t: type[_T], type: str, serializer: Serializable[_T, _D, _T, _D]
    ) -> EventType[_T, _D]:
        return EventType(f"{self._key}:{type}", serializer)

    def define_endpoint_type[
        Req, Res, ReqData, ResData
    ](
        self,
        _req: type[Req] | None,
        _res: type[Res] | None,
        type: str,
        serializer: Serializable[Req, ReqData, Res, ResData],
    ) -> EndpointType[Req, Res, ReqData, ResData]:
        return EndpointType(f"{self._key}:{type}", serializer)

    def dependencies(self) -> List[ExtensionType]:
        return self._dependencies


def define_extension_type[
    T: ServerExtension
](
    key: str,
    create: Callable[[Server], T],
    dependencies: Callable[[], List[ExtensionType]],
):
    return ExtensionType(key, create, dependencies())
