from typing import Any

import httpx

from omu.connection import Address
from omu.endpoint import Endpoint, EndpointType


class HttpEndpoint(Endpoint):
    def __init__(self, address: Address):
        self._address = address

    @property
    def address(self) -> Address:
        return self._address

    async def execute[
        Req, Res
    ](self, type: EndpointType[Req, Res, Any, Any], data: Req) -> Res:
        endpoint_url = self._endpoint_url(type)
        json = type.serializer.serialize(data)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(endpoint_url, json=json)
                response.raise_for_status()
                return type.serializer.deserialize(response.json())
        except httpx.HTTPError as e:
            raise Exception(f"Failed to execute endpoint {type.key}") from e

    def _endpoint_url(self, endpoint: EndpointType) -> str:
        protocol = "https" if self._address.secure else "http"
        host, port = self._address.host, self._address.port
        return f"{protocol}://{host}:{port}/api/v1/{endpoint.key}"
