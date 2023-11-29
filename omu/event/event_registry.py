from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Dict, List

from loguru import logger

if TYPE_CHECKING:
    from omu.client import Client
    from omu.event import EventJson, EventType


type AsyncCallable[T] = Callable[[T], Coroutine[Any, Any, None]]


class EventRegistry(abc.ABC):
    @abc.abstractmethod
    def register(self, *types: EventType) -> None:
        ...

    @abc.abstractmethod
    def add_listener[
        T
    ](
        self,
        event_type: EventType[T, Any],
        listener: AsyncCallable[T] | None = None,
    ) -> Callable[[AsyncCallable[T]], None]:
        ...

    @abc.abstractmethod
    def remove_listener(
        self, event_type: EventType, listener: Callable[[Any], None]
    ) -> None:
        ...


class EventEntry[T, D]:
    def __init__(
        self,
        event_type: EventType[T, D],
        listeners: List[AsyncCallable[T]],
    ):
        self.event_type = event_type
        self.listeners = listeners


def create_event_registry(client: Client) -> EventRegistry:
    class EventRegistryImpl(EventRegistry):
        def __init__(self):
            self._events: Dict[str, EventEntry] = {}

        def register(self, *types: EventType) -> None:
            for type in types:
                if self._events.get(type.type):
                    raise ValueError(f"Event type {type.type} already registered")
                self._events[type.type] = EventEntry(type, [])

        def add_listener[
            T
        ](
            self,
            event_type: EventType[T, Any],
            listener: AsyncCallable[T] | None = None,
        ) -> Callable[[AsyncCallable[T]], None]:
            if not self._events.get(event_type.type):
                raise ValueError(f"Event type {event_type.type} not registered")

            def decorator(listener: AsyncCallable[T]) -> None:
                self._events[event_type.type].listeners.append(listener)

            if listener:
                decorator(listener)
            return decorator

        def remove_listener(
            self, event_type: EventType, listener: AsyncCallable[Any]
        ) -> None:
            if not self._events.get(event_type.type):
                raise ValueError(f"Event type {event_type.type} not registered")
            self._events[event_type.type].listeners.remove(listener)

        async def on_event(self, event_json: EventJson) -> None:
            event = self._events.get(event_json.type)
            if not event:
                logger.warning(f"Received unknown event type {event_json.type}")
                return
            data = event.event_type.serializer.deserialize(event_json.data)
            for listener in event.listeners:
                await listener(data)

    registry = EventRegistryImpl()
    client.connection.add_listener(registry)
    return registry
