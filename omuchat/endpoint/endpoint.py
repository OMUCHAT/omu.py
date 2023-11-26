from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from omuchat.connection import Address
    from omuchat.interface.serializer import Serializer


class EndpointType[ReqType, ResType, ReqData, ResData]():
    def __init__(
        self, key: str, serializer: Serializer[ReqType, ReqData, ResType, ResData]
    ):
        self._key = key
        self._serializer = serializer

    @property
    def key(self) -> str:
        return self._key

    @property
    def serializer(self) -> Serializer[ReqType, ReqData, ResType, ResData]:
        return self._serializer


class Endpoint(abc.ABC):
    @property
    @abc.abstractmethod
    def address(self) -> Address:
        ...

    @abc.abstractmethod
    async def execute[
        Req, Res
    ](self, type: EndpointType[Req, Res, Any, Any], data: Req) -> Res:
        ...
