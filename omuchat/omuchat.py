from omu import OmuClient
from omu.connection import Connection
from omu.endpoint import Endpoint
from omu.event import EventRegistry
from omu.extension import ExtensionRegistry
from omu.extension.server.model.app import App


class Client(OmuClient):
    def __init__(
        self,
        app: App,
        connection: Connection,
        endpoint: Endpoint | None = None,
        event_registry: EventRegistry | None = None,
        extension_registry: ExtensionRegistry | None = None,
    ):
        super().__init__(
            app=app,
            connection=connection,
            endpoint=endpoint,
            event_registry=event_registry,
            extension_registry=extension_registry,
        )
