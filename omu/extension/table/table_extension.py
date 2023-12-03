from typing import Any, AsyncIterator, Dict, List, TypedDict

from omu.client.client import Client
from omu.connection import ConnectionListener
from omu.event.event import ExtensionEventType
from omu.extension.endpoint.endpoint import ClientEndpointType
from omu.extension.endpoint.model.endpoint_info import EndpointInfo
from omu.extension.extension import Extension, define_extension_type
from omu.extension.server.model.extension_info import ExtensionInfo
from omu.extension.table.model.table_info import TableInfo, TableInfoJson
from omu.extension.table.table import ModelTableType, Table, TableListener, TableType
from omu.interface import Keyable, Serializer


class TableExtension(Extension):
    def __init__(self, client: Client):
        self._client = client
        self._tables: Dict[str, Table] = {}
        self.tables = self.register(TablesTableType)
        client.events.register(
            TableRegisterEvent,
            TableItemAddEvent,
            TableItemUpdateEvent,
            TableItemRemoveEvent,
            TableItemClearEvent,
        )

    def register[K: Keyable](self, type: TableType[K, Any]) -> Table[K]:
        if type.info.key() in self._tables:
            raise Exception(f"Table for key {type.info.key()} already registered")
        table = TableImpl(self._client, type)
        self._tables[type.info.key()] = table
        return table

    def get[K: Keyable](self, type: TableType[K, Any]) -> Table[K]:
        if type.info.key() not in self._tables:
            raise Exception(f"Table for key {type.info.key()} not registered")
        return self._tables[type.info.key()]


TableExtensionType = define_extension_type(
    ExtensionInfo.create("table"), lambda client: TableExtension(client), lambda: []
)
TableRegisterEvent = ExtensionEventType[TableInfo, TableInfoJson](
    TableExtensionType, "register", Serializer.model(TableInfo.from_json)
)


class TableReq(TypedDict):
    type: str


class TableItemsReq(TypedDict):
    items: Dict[str, Any]
    type: str


class TableKeysReq(TypedDict):
    type: str
    items: List[str]


TableItemAddEvent = ExtensionEventType[TableItemsReq, TableItemsReq](
    TableExtensionType, "item_add", Serializer.noop()
)
TableItemUpdateEvent = ExtensionEventType[TableItemsReq, TableItemsReq](
    TableExtensionType, "item_update", Serializer.noop()
)
TableItemRemoveEvent = ExtensionEventType[TableItemsReq, TableItemsReq](
    TableExtensionType, "item_remove", Serializer.noop()
)
TableItemClearEvent = ExtensionEventType[TableReq, TableReq](
    TableExtensionType, "item_clear", Serializer.noop()
)

TableItemGetEndpoint = ClientEndpointType[TableKeysReq, TableItemsReq](
    EndpointInfo.create(TableExtensionType, "item_get"),
)


class TableFetchReq(TypedDict):
    type: str
    limit: int
    cursor: str | None


TableItemFetchEndpoint = ClientEndpointType[TableFetchReq, Dict[str, Any]](
    EndpointInfo.create(TableExtensionType, "item_fetch"), Serializer.noop()
)
TableItemSizeEndpoint = ClientEndpointType[TableReq, int](
    EndpointInfo.create(TableExtensionType, "item_size"), Serializer.noop()
)
TablesTableType = ModelTableType[TableInfo, TableInfoJson](
    TableInfo.create(TableExtensionType, "tables"),
    Serializer.model(lambda data: TableInfo.from_json(data)),
)


class TableImpl[T: Keyable](Table[T], ConnectionListener):
    def __init__(self, client: Client, type: TableType[T, Any]):
        self._client = client
        self._type = type
        self._cache: Dict[str, T] = {}
        self._listeners: List[TableListener[T]] = []
        self.key = type.info.key()

        client.events.add_listener(TableItemAddEvent, self._on_item_add)
        client.events.add_listener(TableItemUpdateEvent, self._on_item_update)
        client.events.add_listener(TableItemRemoveEvent, self._on_item_remove)
        client.events.add_listener(TableItemClearEvent, self._on_item_clear)
        client.connection.add_listener(self)

    @property
    def cache(self) -> Dict[str, T]:
        return self._cache

    async def on_connected(self) -> None:
        await self._client.send(TableRegisterEvent, self._type.info)

    async def get(self, key: str) -> T | None:
        if key in self._cache:
            return self._cache[key]
        res = await self._client.endpoints.call(
            TableItemGetEndpoint, TableKeysReq(type=self.key, items=[key])
        )
        items = self._parse_items(res["items"])
        self._cache.update(items)
        if key in items:
            return items[key]
        return None

    async def add(self, *items: T) -> None:
        data = {item.key(): self._type.serializer.serialize(item) for item in items}
        await self._client.send(
            TableItemAddEvent, TableItemsReq(type=self.key, items=data)
        )

    async def set(self, *items: T) -> None:
        data = {item.key(): self._type.serializer.serialize(item) for item in items}
        await self._client.send(
            TableItemUpdateEvent, TableItemsReq(type=self.key, items=data)
        )

    async def remove(self, *items: T) -> None:
        data = {item.key(): self._type.serializer.serialize(item) for item in items}
        await self._client.send(
            TableItemRemoveEvent, TableItemsReq(type=self.key, items=data)
        )

    async def clear(self) -> None:
        await self._client.send(TableItemClearEvent, TableReq(type=self.key))

    async def fetch(self, limit: int = 100, cursor: str | None = None) -> Dict[str, T]:
        res = await self._client.endpoints.call(
            TableItemFetchEndpoint,
            TableFetchReq(type=self.key, limit=limit, cursor=cursor),
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
        res = await self._client.endpoints.call(
            TableItemSizeEndpoint, TableReq(type=self.key)
        )
        return res

    def add_listener(self, listener: TableListener[T]) -> None:
        self._listeners.append(listener)

    def remove_listener(self, listener: TableListener[T]) -> None:
        self._listeners.remove(listener)

    async def _on_item_add(self, event: TableItemsReq) -> None:
        if event["type"] != self.key:
            return
        items = self._parse_items(event["items"])
        self._cache.update(items)
        for listener in self._listeners:
            await listener.on_add(items)
            await listener.on_cache_update(self._cache)

    async def _on_item_update(self, event: TableItemsReq) -> None:
        if event["type"] != self.key:
            return
        items = self._parse_items(event["items"])
        self._cache.update(items)
        for listener in self._listeners:
            await listener.on_update(items)
            await listener.on_cache_update(self._cache)

    async def _on_item_remove(self, event: TableItemsReq) -> None:
        if event["type"] != self.key:
            return
        items = self._parse_items(event["items"])
        for key in items.keys():
            if key not in self._cache:
                continue
            del self._cache[key]
        for listener in self._listeners:
            await listener.on_remove(items)
            await listener.on_cache_update(self._cache)

    async def _on_item_clear(self, event: TableReq) -> None:
        if event["type"] != self.key:
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
