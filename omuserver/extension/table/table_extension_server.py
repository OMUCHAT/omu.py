from typing import Any, Dict

from omu.extension.table.model.table_info import TableInfo
from omu.extension.table.table_extension import (
    TableFetchReq,
    TableItemAddEvent,
    TableItemClearEvent,
    TableItemFetchEndpoint,
    TableItemRemoveEvent,
    TableItemSetEvent,
    TableRegisterEvent,
)
from omu.interface.serializable import Serializer
from omuserver.extension.extension import Extension
from omuserver.extension.table.dict_table import DictTable
from omuserver.extension.table.sqlitedict_table import SqlitedictTable
from omuserver.extension.table.table_server import TableServer
from omuserver.server import Server
from omuserver.session.session import Session


class TableExtensionServer(Extension):
    def __init__(self, server: Server) -> None:
        self._server = server
        self._tables: Dict[str, TableServer] = {}
        server.network.bind_endpoint(TableItemFetchEndpoint, self._on_table_item_fetch)
        server.events.register(
            TableRegisterEvent,
            TableItemAddEvent,
            TableItemSetEvent,
            TableItemRemoveEvent,
            TableItemClearEvent,
        )
        server.events.add_listener(TableRegisterEvent, self._on_table_register)

    async def _on_table_item_fetch(self, req: TableFetchReq) -> Dict[str, Any]:
        table = self._tables.get(req["type"], None)
        if table is None:
            return {}
        items = await table.fetch(req["limit"], req.get("cursor"))
        return {key: table.serializer.serialize(item) for key, item in items.items()}

    async def _on_table_register(self, session: Session, info: TableInfo) -> None:
        if info.key() in self._tables:
            table = self._tables[info.key()]
            table.attach_session(session)
            return
        path = self._server.data_path / "tables" / info.key()
        if info.use_database:
            table = SqlitedictTable(self._server, path, info, Serializer.noop())
        else:
            table = DictTable(self._server, path, info, Serializer.noop())
        self._tables[info.key()] = table
        table.attach_session(session)

    def initialize(self) -> None:
        pass

    def stop(self) -> None:
        pass
