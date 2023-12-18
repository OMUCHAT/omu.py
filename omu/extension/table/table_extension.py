from typing import Any, AsyncIterator, Awaitable, Callable, Dict, List, TypedDict

from omu.client.client import Client
from omu.connection import ConnectionListener
from omu.event.event import ExtensionEventType
from omu.extension.endpoint.endpoint import ClientEndpointType
from omu.extension.endpoint.model.endpoint_info import EndpointInfo
from omu.extension.extension import Extension, define_extension_type
from omu.extension.server.model.extension_info import ExtensionInfo
from omu.interface import Keyable, Serializer

from .model.table_info import TableInfo, TableInfoJson
from .table import (
    AsyncCallback,
    CallbackTableListener,
    ModelTableType,
    Table,
    TableListener,
    TableType,
)

type Coro[**P, T] = Callable[P, Awaitable[T]]


class TableExtension(Extension):
    def __init__(self, client: Client):
        self._client = client
        self._tables: Dict[str, Table] = {}
        client.events.register(
            TableRegisterEvent,
            TableListenEvent,
            TableProxyListenEvent,
            TableProxyEvent,
            TableItemAddEvent,
            TableItemUpdateEvent,
            TableItemRemoveEvent,
            TableItemClearEvent,
        )
        self.tables = self.get(TablesTableType)

    def register[K: Keyable](self, type: TableType[K, Any]) -> Table[K]:
        if self.has(type):
            raise Exception(f"Table for key {type.info.key()} already registered")
        table = TableImpl(self._client, type, owner=True)
        self._tables[type.info.key()] = table
        return table

    def get[K: Keyable](self, type: TableType[K, Any]) -> Table[K]:
        if self.has(type):
            return self._tables[type.info.key()]
        table = TableImpl(self._client, type)
        self._tables[type.info.key()] = table
        return table

    def has(self, type: TableType[Any, Any]) -> bool:
        return type.info.key() in self._tables


TableExtensionType = define_extension_type(
    ExtensionInfo.create("table"), lambda client: TableExtension(client), lambda: []
)


class TableEventData(TypedDict):
    type: str


class TableItemsEventData(TypedDict):
    items: Dict[str, Any]
    type: str


class TableProxyEventData(TypedDict):
    items: Dict[str, Any]
    type: str
    key: int


class TableKeysEventData(TypedDict):
    type: str
    items: List[str]


TableRegisterEvent = ExtensionEventType[TableInfo, TableInfoJson](
    TableExtensionType, "register", Serializer.model(TableInfo.from_json)
)
TableListenEvent = ExtensionEventType[str, str](
    TableExtensionType, "listen", Serializer.noop()
)
TableProxyListenEvent = ExtensionEventType[str, str](
    TableExtensionType, "proxy_listen", Serializer.noop()
)
TableProxyEvent = ExtensionEventType[TableProxyEventData, TableProxyEventData](
    TableExtensionType, "proxy", Serializer.noop()
)
TableProxyEndpoint = ClientEndpointType[TableProxyEventData, int](
    EndpointInfo.create(TableExtensionType, "proxy"),
)


TableItemAddEvent = ExtensionEventType[TableItemsEventData, TableItemsEventData](
    TableExtensionType, "item_add", Serializer.noop()
)
TableItemUpdateEvent = ExtensionEventType[TableItemsEventData, TableItemsEventData](
    TableExtensionType, "item_update", Serializer.noop()
)
TableItemRemoveEvent = ExtensionEventType[TableItemsEventData, TableItemsEventData](
    TableExtensionType, "item_remove", Serializer.noop()
)
TableItemClearEvent = ExtensionEventType[TableEventData, TableEventData](
    TableExtensionType, "item_clear", Serializer.noop()
)

TableItemGetEndpoint = ClientEndpointType[TableKeysEventData, TableItemsEventData](
    EndpointInfo.create(TableExtensionType, "item_get"),
)


class TableFetchReq(TypedDict):
    type: str
    limit: int
    cursor: str | None


TableItemFetchEndpoint = ClientEndpointType[TableFetchReq, Dict[str, Any]](
    EndpointInfo.create(TableExtensionType, "item_fetch"), Serializer.noop()
)
TableItemSizeEndpoint = ClientEndpointType[TableEventData, int](
    EndpointInfo.create(TableExtensionType, "item_size"), Serializer.noop()
)
TablesTableType = ModelTableType[TableInfo, TableInfoJson](
    TableInfo.create(TableExtensionType, "tables"),
    Serializer.model(lambda data: TableInfo.from_json(data)),
)


class TableImpl[T: Keyable](Table[T], ConnectionListener):
    def __init__(self, client: Client, type: TableType[T, Any], owner: bool = False):
        self._client = client
        self._type = type
        self._owner = owner
        self._cache: Dict[str, T] = {}
        self._listeners: List[TableListener[T]] = []
        self._proxies: List[Coro[[T], T | None]] = []
        self.key = type.info.key()
        self._listening = False

        client.events.add_listener(TableProxyEvent, self._on_proxy)
        client.events.add_listener(TableItemAddEvent, self._on_item_add)
        client.events.add_listener(TableItemUpdateEvent, self._on_item_update)
        client.events.add_listener(TableItemRemoveEvent, self._on_item_remove)
        client.events.add_listener(TableItemClearEvent, self._on_item_clear)
        client.connection.add_listener(self)

    @property
    def cache(self) -> Dict[str, T]:
        return self._cache

    async def get(self, key: str) -> T | None:
        if key in self._cache:
            return self._cache[key]
        res = await self._client.endpoints.call(
            TableItemGetEndpoint, TableKeysEventData(type=self.key, items=[key])
        )
        items = self._parse_items(res["items"])
        self._cache.update(items)
        if key in items:
            return items[key]
        return None

    async def add(self, *items: T) -> None:
        data = {item.key(): self._type.serializer.serialize(item) for item in items}
        await self._client.send(
            TableItemAddEvent, TableItemsEventData(type=self.key, items=data)
        )

    async def update(self, *items: T) -> None:
        data = {item.key(): self._type.serializer.serialize(item) for item in items}
        await self._client.send(
            TableItemUpdateEvent, TableItemsEventData(type=self.key, items=data)
        )

    async def remove(self, *items: T) -> None:
        data = {item.key(): self._type.serializer.serialize(item) for item in items}
        await self._client.send(
            TableItemRemoveEvent, TableItemsEventData(type=self.key, items=data)
        )

    async def clear(self) -> None:
        await self._client.send(TableItemClearEvent, TableEventData(type=self.key))

    async def fetch(self, limit: int = 100, cursor: str | None = None) -> Dict[str, T]:
        res = await self._client.endpoints.call(
            TableItemFetchEndpoint,
            TableFetchReq(type=self.key, limit=limit or 100, cursor=cursor),
        )
        items = self._parse_items(res)
        self._cache.update(items)
        for listener in self._listeners:
            await listener.on_cache_update(self._cache)
        return items

    async def iter(self) -> AsyncIterator[T]:
        cursor: str | None = None
        while True:
            items = {
                k: v for k, v in (await self.fetch(100, cursor)).items() if k != cursor
            }
            if len(items) == 0:
                break
            for item in items.values():
                yield item
            *_, cursor = items.keys()
            if cursor is None:
                break

    async def size(self) -> int:
        res = await self._client.endpoints.call(
            TableItemSizeEndpoint, TableEventData(type=self.key)
        )
        return res

    def add_listener(self, listener: TableListener[T]) -> None:
        self._listeners.append(listener)
        self._listening = True

    def remove_listener(self, listener: TableListener[T]) -> None:
        self._listeners.remove(listener)

    def listen(
        self, callback: AsyncCallback[Dict[str, T]] | None = None
    ) -> Callable[[], None]:
        self._listening = True
        listener = CallbackTableListener(on_cache_update=callback)
        self._listeners.append(listener)
        return lambda: self._listeners.remove(listener)

    def proxy(self, callback: Coro[[T], T | None]) -> Callable[[], None]:
        self._proxies.append(callback)
        return lambda: self._proxies.remove(callback)

    async def on_connected(self) -> None:
        if self._owner:
            await self._client.send(TableRegisterEvent, self._type.info)
        if self._listening:
            await self._client.send(TableListenEvent, self.key)
            if self._type.info.cache_size:
                await self.fetch(self._type.info.cache_size)
        if len(self._proxies) > 0:
            await self._client.send(TableProxyListenEvent, self.key)

    async def _on_proxy(self, event: TableProxyEventData) -> None:
        if event["type"] != self.key:
            return
        items = self._parse_items(event["items"])
        for proxy in self._proxies:
            for key, item in items.items():
                if item := await proxy(item):
                    items[key] = item
                else:
                    del items[key]
        await self._client.endpoints.execute(
            TableProxyEndpoint,
            TableProxyEventData(
                type=self.key,
                key=event["key"],
                items={
                    item.key(): self._type.serializer.serialize(item)
                    for item in items.values()
                },
            ),
        )

    async def _on_item_add(self, event: TableItemsEventData) -> None:
        if event["type"] != self.key:
            return
        items = self._parse_items(event["items"])
        self._cache.update(items)
        for listener in self._listeners:
            await listener.on_add(items)
            await listener.on_cache_update(self._cache)

    async def _on_item_update(self, event: TableItemsEventData) -> None:
        if event["type"] != self.key:
            return
        items = self._parse_items(event["items"])
        self._cache.update(items)
        for listener in self._listeners:
            await listener.on_update(items)
            await listener.on_cache_update(self._cache)

    async def _on_item_remove(self, event: TableItemsEventData) -> None:
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

    async def _on_item_clear(self, event: TableEventData) -> None:
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
