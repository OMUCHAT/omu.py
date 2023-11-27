from omu.client import Client
from omu.extension.extension import Extension, define_extension_type
from omu.extension.server.model.app import App, AppJson
from omu.extension.table import TableExtensionType, define_table_type_model

ServerExtensionType = define_extension_type(
    "server", lambda client: ServerExtension(client), lambda: []
)

AppsListKey = define_table_type_model(
    ServerExtensionType, "apps", App, AppJson, lambda data: App.from_json(data)
)


class ServerExtension(Extension):
    def __init__(self, client: Client) -> None:
        self.client = client
        tables = client.extensions.get(TableExtensionType)
        self.apps = tables.register(AppsListKey)
