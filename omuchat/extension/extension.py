from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Callable, List

from omuchat.endpoint import EndpointType
from omuchat.event import EventType

if TYPE_CHECKING:
    from omuchat.client import Client
    from omuchat.interface.serializer import Serializer


class Extension(abc.ABC):
    pass


class ExtensionType[T: Extension]():
    def __init__(
        self, key: str, create: Callable[[Client], T], dependencies: List[ExtensionType]
    ):
        self._key = key
        self._create = create
        self._dependencies = dependencies

    @property
    def key(self) -> str:
        return self._key

    def create(self, client: Client) -> T:
        return self._create(client)

    def define_event_type[
        _T, _D
    ](
        self, _t: type[_T], type: str, serializer: Serializer[_T, _D, _T, _D]
    ) -> EventType[_T, _D]:
        return EventType(f"{self._key}:{type}", serializer)

    def define_endpoint_type[
        Req, Res, ReqData, ResData
    ](
        self,
        _req: type[Req] | None,
        _res: type[Res] | None,
        type: str,
        serializer: Serializer[Req, ReqData, Res, ResData],
    ) -> EndpointType[Req, Res, ReqData, ResData]:
        return EndpointType(f"{self._key}:{type}", serializer)

    def dependencies(self) -> List[ExtensionType]:
        return self._dependencies


def define_extension_type[
    T: Extension
](
    key: str,
    create: Callable[[Client], T],
    dependencies: Callable[[], List[ExtensionType]],
):
    return ExtensionType(key, create, dependencies())
