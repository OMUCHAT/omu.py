from typing import Any, Dict

from omu.extension.table.model.table_info import TableInfo
from omu.extension.table.table_extension import (
    TableItemAddEvent,
    TableItemClearEvent,
    TableItemRemoveEvent,
    TableItemSetEvent,
    TableItemsReq,
    TableReq,
)
from omuserver.extension.table.table_server import TableListener
from omuserver.session.session import Session


class SessionTableHandler(TableListener):
    def __init__(self, info: TableInfo, session: Session):
        self._info = info
        self._session = session

    async def on_add(self, items: Dict[str, Any]) -> None:
        await self._session.send(
            TableItemAddEvent, TableItemsReq(items=items, type=self._info.key())
        )

    async def on_set(self, items: Dict[str, Any]) -> None:
        await self._session.send(
            TableItemSetEvent, TableItemsReq(items=items, type=self._info.key())
        )

    async def on_remove(self, items: Dict[str, Any]) -> None:
        await self._session.send(
            TableItemRemoveEvent,
            TableItemsReq(items=items, type=self._info.key()),
        )

    async def on_clear(self) -> None:
        await self._session.send(TableItemClearEvent, TableReq(type=self._info.key()))
