from pathlib import Path
from typing import AsyncIterator, Dict

from omu.extension.table.model.table_info import TableInfo
from omu.extension.table.table_extension import (
    TableItemAddEvent,
    TableItemClearEvent,
    TableItemRemoveEvent,
    TableItemSetEvent,
    TableItemsReq,
    TableReq,
)
from omu.interface.serializable import Serializable
from omuserver.extension.table.session_table_handler import SessionTableHandler
from omuserver.server import Server
from omuserver.session.session import Session, SessionListener

from .table_server import TableListener, TableServer


class DictTable[T](TableServer[T], SessionListener):
    def __init__(
        self,
        server: Server,
        path: Path,
        info: TableInfo,
        serializer: Serializable[T, dict],
    ):
        self._server = server
        self._path = path
        self._info = info
        self._serializer = serializer
        self._cache: Dict[str, T] = {}
        self._listeners: list[TableListener[T]] = []
        self._handlers: Dict[Session, SessionTableHandler] = {}
        server.events.add_listener(
            TableItemAddEvent,
            self._on_table_item_add,
        )
        server.events.add_listener(
            TableItemSetEvent,
            self._on_table_item_set,
        )
        server.events.add_listener(
            TableItemRemoveEvent,
            self._on_table_item_remove,
        )
        server.events.add_listener(
            TableItemClearEvent,
            self._on_table_item_clear,
        )

    async def _on_table_item_add(self, session: Session, items: TableItemsReq) -> None:
        if items["type"] != self._info.key():
            return
        await self.add(items["items"])

    async def _on_table_item_set(self, session: Session, items: TableItemsReq) -> None:
        if items["type"] != self._info.key():
            return
        await self.set(items["items"])

    async def _on_table_item_remove(
        self, session: Session, items: TableItemsReq
    ) -> None:
        if items["type"] != self._info.key():
            return
        await self.remove(list(items["items"].keys()))

    async def _on_table_item_clear(self, session: Session, req: TableReq) -> None:
        if req["type"] != self._info.key():
            return
        await self.clear()

    @property
    def cache(self) -> Dict[str, T]:
        return self._cache

    @property
    def serializer(self) -> Serializable[T, dict]:
        return self._serializer

    def attach_session(self, session: Session) -> None:
        handler = SessionTableHandler(self._info, session)
        self._handlers[session] = handler
        self.add_listener(handler)
        session.add_listener(self)

    async def on_disconnected(self, session: Session) -> None:
        handler = self._handlers.pop(session)
        self.remove_listener(handler)

    async def get(self, key: str) -> T | None:
        return self._cache.get(key, None)

    async def add(self, items: Dict[str, T]) -> None:
        self._cache.update(items)
        for listener in self._listeners:
            await listener.on_cache_update(self._cache)
            await listener.on_add(items)

    async def set(self, items: Dict[str, T]) -> None:
        self._cache.update(items)
        for listener in self._listeners:
            await listener.on_cache_update(self._cache)
            await listener.on_set(items)

    async def remove(self, items: list[str]) -> None:
        removed_items: Dict[str, T] = {}
        for key in items:
            if key in self._cache:
                removed_items[key] = self._cache[key]
                del self._cache[key]
        for listener in self._listeners:
            await listener.on_cache_update(self._cache)
            await listener.on_remove(removed_items)

    async def clear(self) -> None:
        self._cache.clear()
        for listener in self._listeners:
            await listener.on_cache_update(self._cache)
            await listener.on_clear()

    async def fetch(self, limit: int = 100, cursor: str | None = None) -> Dict[str, T]:
        items = {}
        keys = list(self._cache.keys())
        if cursor is not None:
            cursor_index = keys.index(cursor)
            keys = keys[cursor_index:]
        for key in keys[:limit]:
            items[key] = self._cache[key]
        return items

    async def iterator(self) -> AsyncIterator[T]:
        cursor: str | None = None
        while True:
            items = await self.fetch(100, cursor)
            if len(items) == 0:
                break
            for item in items.values():
                yield item
            *_, cursor = items.keys()

    async def size(self) -> int:
        return len(self._cache)

    def add_listener(self, listener: TableListener[T]) -> None:
        self._listeners.append(listener)

    def remove_listener(self, listener: TableListener[T]) -> None:
        self._listeners.remove(listener)
