from omu.client import Client
from omu.extension.extension import Extension, define_extension_type
from omu.extension.server.model.app import App, AppJson
from omu.extension.server.model.extension_info import ExtensionInfo, ExtensionInfoJson
from omu.extension.table import TableExtensionType
from omu.extension.table.model.table_info import TableInfo
from omu.extension.table.table import ModelTableType
from omu.interface import Serializer

ServerExtensionType = define_extension_type(
    ExtensionInfo.create("server"), lambda client: ServerExtension(client), lambda: []
)

AppsTableType = ModelTableType[App, AppJson](
    TableInfo.create(ServerExtensionType, "apps"),
    Serializer.model(lambda data: App.from_json(data)),
)
ExtensionsTableType = ModelTableType[ExtensionInfo, ExtensionInfoJson](
    TableInfo.create(ServerExtensionType, "extensions"),
    Serializer.model(lambda data: ExtensionInfo.from_json(data)),
)


class ServerExtension(Extension):
    def __init__(self, client: Client) -> None:
        self.client = client
        tables = client.extensions.get(TableExtensionType)
        self.apps = tables.get(AppsTableType)
        self.extensions = tables.get(ExtensionsTableType)
