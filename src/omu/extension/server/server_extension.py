from omu.client import Client
from omu.extension.endpoint import JsonEndpointType
from omu.extension.extension import Extension, define_extension_type
from omu.extension.server.model.app import App, AppJson
from omu.extension.server.model.extension_info import ExtensionInfo, ExtensionInfoJson
from omu.extension.table import TableExtensionType
from omu.extension.table.table import ModelTableType

ServerExtensionType = define_extension_type(
    ExtensionInfo.create("server"), lambda client: ServerExtension(client), lambda: []
)

AppsTableType = ModelTableType[App, AppJson].of_extension(
    ServerExtensionType,
    "apps",
    App,
)
ExtensionsTableType = ModelTableType[ExtensionInfo, ExtensionInfoJson].of_extension(
    ServerExtensionType,
    "extensions",
    ExtensionInfo,
)
ShutdownEndpointType = JsonEndpointType[bool, bool].of_extension(
    ServerExtensionType,
    "shutdown",
)


class ServerExtension(Extension):
    def __init__(self, client: Client) -> None:
        self.client = client
        tables = client.extensions.get(TableExtensionType)
        self.apps = tables.get(AppsTableType)
        self.extensions = tables.get(ExtensionsTableType)

    async def shutdown(self, restart: bool = False) -> bool:
        return await self.client.endpoints.call(ShutdownEndpointType, restart)
