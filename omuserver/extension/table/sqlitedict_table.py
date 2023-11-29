from pathlib import Path
from typing import Any, AsyncIterator, Dict, List

import sqlitedict

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
from omuserver.session.session import Session, SessionListener

from .table_server import TableListener, TableServer


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


class SqlitedictTable[T](TableServer[T], SessionListener):
    def __init__(self, path: Path, info: TableInfo, serializer: Serializable[T, Any]):
        self._path = path
        self._info = info
        self._serializer = serializer
        self._db = sqlitedict.SqliteDict(path / "data.db", autocommit=True)
        self._use_cache = info.cache or False
        self._cache: Dict[str, T] = {}
        self._cache_size = info.cache_size or 1000
        self._listeners: List[TableListener] = []
        self._handlers: Dict[Session, SessionTableHandler] = {}

    @property
    def cache(self) -> Dict[str, T]:
        return self._cache

    @property
    def serializer(self) -> Serializable[T, Any]:
        return self._serializer

    def attach_session(self, session: Session) -> None:
        handler = SessionTableHandler(self._info, session)
        self._handlers[session] = handler
        self.add_listener(handler)
        session.add_listener(self)

    async def on_disconnected(self, session: Session) -> None:
        handler = self._handlers.pop(session)
        self.remove_listener(handler)

    async def _add_to_cache(self, items: Dict[str, T]) -> None:
        if not self._use_cache:
            return
        for key, item in items.items():
            self._cache[key] = item
            if len(self._cache) > self._cache_size:
                del self._cache[next(iter(self._cache))]
        for listener in self._listeners:
            await listener.on_cache_update(self._cache)

    async def get(self, key: str) -> T | None:
        if key in self._cache:
            return self._cache[key]
        if key in self._db:
            item = self._serializer.deserialize(self._db[key])
            await self._add_to_cache({key: item})
            return item
        return None

    async def add(self, items: Dict[str, T]) -> None:
        for key, item in items.items():
            self._db[key] = self._serializer.serialize(item)
        await self._add_to_cache(items)
        for listener in self._listeners:
            await listener.on_add(items)

    async def set(self, items: Dict[str, T]) -> None:
        for key, item in items.items():
            self._db[key] = self._serializer.serialize(item)
        await self._add_to_cache(items)
        for listener in self._listeners:
            await listener.on_set(items)

    async def remove(self, items: list[str]) -> None:
        removed_items: Dict[str, T] = {}
        for key in items:
            if key in self._db:
                item = self._serializer.deserialize(self._db[key])
                del self._db[key]
                removed_items[key] = item
            if key in self._cache:
                del self._cache[key]
        for listener in self._listeners:
            await listener.on_remove(removed_items)

    async def clear(self) -> None:
        self._db.clear()
        self._cache.clear()
        for listener in self._listeners:
            await listener.on_clear()

    async def fetch(self, limit: int = 100, cursor: str | None = None) -> Dict[str, T]:
        items: Dict[str, T] = {}
        keys = list(self._db.keys())
        if cursor is not None:
            cursor_index = keys.index(cursor)
            keys = keys[cursor_index + 1 :]
        for key in keys[:limit]:
            item = self._serializer.deserialize(self._db[key])
            items[key] = item

        await self._add_to_cache(items)
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
        return len(self._db)

    async def close(self) -> None:
        self._db.close()

    def add_listener(self, listener: TableListener[T]) -> None:
        self._listeners.append(listener)

    def remove_listener(self, listener: TableListener[T]) -> None:
        self._listeners.remove(listener)
