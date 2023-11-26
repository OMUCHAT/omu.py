from omuchat.client import Client, ClientListener
from omuchat.extension import Extension, define_extension_type
from omuchat.extension.chat.model.channel import Channel, ChannelJson
from omuchat.extension.chat.model.message import Message, MessageJson
from omuchat.extension.chat.model.provider import Provider, ProviderJson
from omuchat.extension.chat.model.room import Room, RoomJson
from omuchat.extension.table import TableExtensionType, define_table_type_model


class ChatExtension(Extension, ClientListener):
    def __init__(self, client: Client) -> None:
        self.client = client
        client.add_listener(self)
        tables = client.extensions.get(TableExtensionType)
        self.messages = tables.register(MessagesTableKey)
        self.channels = tables.register(ChannelsTableKey)
        self.providers = tables.register(ProviderTableKey)
        self.rooms = tables.register(RoomTableKey)

    async def on_initialized(self) -> None:
        ...


ChatExtensionType = define_extension_type(
    "chat", lambda client: ChatExtension(client), lambda: []
)
MessagesTableKey = define_table_type_model(
    ChatExtensionType,
    "messages",
    Message,
    MessageJson,
    lambda data: Message.from_json(data),
)
ChannelsTableKey = define_table_type_model(
    ChatExtensionType,
    "channels",
    Channel,
    ChannelJson,
    lambda data: Channel.from_json(data),
)
ProviderTableKey = define_table_type_model(
    ChatExtensionType,
    "providers",
    Provider,
    ProviderJson,
    lambda data: Provider.from_json(data),
)
RoomTableKey = define_table_type_model(
    ChatExtensionType,
    "rooms",
    Room,
    RoomJson,
    lambda data: Room.from_json(data),
)
