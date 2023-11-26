from typing import Any, AsyncIterator, Dict, List, TypedDict

from omuchat.client import Client
from omuchat.extension import Extension, define_extension_type
from omuchat.extension.table import Table, TableListener, TableType
from omuchat.interface.keyable import Keyable
from omuchat.interface.serializer import make_pass_serializer


class TableExtension(Extension):
    def __init__(self, client: Client):
        self._client = client
        self._tables: Dict[str, Table] = {}
        client.events.register(
            TableItemAddEvent,
            TableItemSetEvent,
            TableItemRemoveEvent,
            TableItemClearEvent,
        )

    def register[K: Keyable](self, type: TableType[K, Any]) -> Table[K]:
        if type.key in self._tables:
            raise Exception(f"Table for key {type.key} already registered")
        table = TableImpl(self._client, type)
        self._tables[type.key] = table
        return table

    def get[K: Keyable](self, type: TableType[K, Any]) -> Table[K]:
        if type.key not in self._tables:
            raise Exception(f"Table for key {type.key} not registered")
        return self._tables[type.key]


TableExtensionType = define_extension_type(
    "table", lambda client: TableExtension(client), lambda: []
)


class _TableEvent(TypedDict):
    type: str


class _TableItemsEvent(_TableEvent):
    items: Dict[str, Any]


class _TableKeysEvent(_TableEvent):
    items: List[str]


class _TableValuesEvent(_TableEvent):
    items: List[Any]


TableItemAddEvent = TableExtensionType.define_event_type(
    _TableItemsEvent, "item_add", make_pass_serializer()
)
TableItemSetEvent = TableExtensionType.define_event_type(
    _TableItemsEvent, "item_set", make_pass_serializer()
)
TableItemRemoveEvent = TableExtensionType.define_event_type(
    _TableItemsEvent, "item_remove", make_pass_serializer()
)
TableItemClearEvent = TableExtensionType.define_event_type(
    _TableEvent, "item_clear", make_pass_serializer()
)

TableItemGetEndpoint = TableExtensionType.define_endpoint_type(
    _TableKeysEvent, _TableItemsEvent, "item_get", make_pass_serializer()
)


class _TableFetchReq(_TableEvent):
    limit: int
    cursor: str | None


TableItemFetchEndpoint = TableExtensionType.define_endpoint_type(
    _TableFetchReq, Dict[str, Any], "item_fetch", make_pass_serializer()
)
TableItemSizeEndpoint = TableExtensionType.define_endpoint_type(
    None, int, "item_size", make_pass_serializer()
)


class TableImpl[T: Keyable](Table[T]):
    def __init__(self, client: Client, type: TableType[T, Any]):
        self._client = client
        self._type = type
        self._cache: Dict[str, T] = {}
        self._listeners: List[TableListener[T]] = []

        client.events.add_listener(TableItemAddEvent, self._on_item_add)
        client.events.add_listener(TableItemSetEvent, self._on_item_set)
        client.events.add_listener(TableItemRemoveEvent, self._on_item_remove)
        client.events.add_listener(TableItemClearEvent, self._on_item_clear)

    @property
    def cache(self) -> Dict[str, T]:
        return self._cache

    async def get(self, key: str) -> T | None:
        if key in self._cache:
            return self._cache[key]
        res = await self._client.endpoint.execute(
            TableItemGetEndpoint, {"type": self._type.key, "items": [key]}
        )
        items = self._parse_items(res["items"])
        self._cache.update(items)
        if key in items:
            return items[key]
        return None

    async def add(self, *items: T) -> None:
        data = {item.key(): self._type.serializer.serialize(item) for item in items}
        await self._client.send(
            TableItemAddEvent, {"type": self._type.key, "items": data}
        )

    async def set(self, *items: T) -> None:
        data = {item.key(): self._type.serializer.serialize(item) for item in items}
        await self._client.send(
            TableItemSetEvent, {"type": self._type.key, "items": data}
        )

    async def remove(self, *items: T) -> None:
        data = {item.key(): self._type.serializer.serialize(item) for item in items}
        await self._client.send(
            TableItemRemoveEvent, {"type": self._type.key, "items": data}
        )

    async def clear(self) -> None:
        await self._client.send(TableItemClearEvent, {"type": self._type.key})

    async def fetch(self, limit: int = 100, cursor: str | None = None) -> Dict[str, T]:
        res = await self._client.endpoint.execute(
            TableItemFetchEndpoint,
            {"type": self._type.key, "limit": limit, "cursor": cursor},
        )
        items = self._parse_items(res)
        self._cache.update(items)
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
        res = await self._client.endpoint.execute(
            TableItemSizeEndpoint, {"type": self._type.key}
        )
        return res

    async def add_listener(self, listener: TableListener[T]) -> None:
        self._listeners.append(listener)

    async def remove_listener(self, listener: TableListener[T]) -> None:
        self._listeners.remove(listener)

    async def _on_item_add(self, event: _TableItemsEvent) -> None:
        if event["type"] != self._type.key:
            return
        items = self._parse_items(event["items"])
        self._cache.update(items)
        for listener in self._listeners:
            await listener.on_add(items)
            await listener.on_cache_update(self._cache)

    async def _on_item_set(self, event: _TableItemsEvent) -> None:
        if event["type"] != self._type.key:
            return
        items = self._parse_items(event["items"])
        self._cache.update(items)
        for listener in self._listeners:
            await listener.on_set(items)
            await listener.on_cache_update(self._cache)

    async def _on_item_remove(self, event: _TableItemsEvent) -> None:
        if event["type"] != self._type.key:
            return
        items = self._parse_items(event["items"])
        for key in items.keys():
            if key not in self._cache:
                continue
            del self._cache[key]
        for listener in self._listeners:
            await listener.on_remove(items)
            await listener.on_cache_update(self._cache)

    async def _on_item_clear(self, event: _TableEvent) -> None:
        if event["type"] != self._type.key:
            return
        self._cache.clear()
        for listener in self._listeners:
            await listener.on_clear()
            await listener.on_cache_update(self._cache)

    def _parse_items(self, items: Dict[str, Any]) -> Dict[str, T]:
        parsed: Dict[str, T] = {}
        for key, item in items.items():
            item = self._type.serializer.deserialize(item)
            if not item:
                raise Exception(f"Failed to deserialize item {key}")
            parsed[key] = item
        return parsed
