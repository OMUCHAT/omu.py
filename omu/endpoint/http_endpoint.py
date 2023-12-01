from typing import Any

import aiohttp

from omu.connection import Address
from omu.endpoint import Endpoint, EndpointType


class HttpEndpoint(Endpoint):
    def __init__(self, address: Address):
        self._address = address

    @property
    def address(self) -> Address:
        return self._address

    async def execute[Req, Res](
        self, type: EndpointType[Req, Res, Any, Any], data: Req
    ) -> Res:
        endpoint_url = self._endpoint_url(type)
        json = type.request_serializer.serialize(data)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint_url, json=json) as response:
                    response.raise_for_status()
                    return type.response_serializer.deserialize(await response.json())
        except aiohttp.ClientError as e:
            raise Exception(f"Failed to execute endpoint {type.info.key()}") from e

    def _endpoint_url(self, endpoint: EndpointType) -> str:
        protocol = "https" if self._address.secure else "http"
        host, port = self._address.host, self._address.port
        return f"{protocol}://{host}:{port}/api/v1/{endpoint.info.key()}"
