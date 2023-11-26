import asyncio

from omuchat import Address, OmuClient, WebsocketConnection
from omuchat.connection import ConnectionListener
from omuchat.event.events import Ready
from omuchat.extension.chat.chat_extension import ChatExtensionType
from omuchat.extension.server.model.app import App
from omuchat.helper import instance

address = Address(
    host="localhost",
    port=26423,
    secure=False,
)
connection = WebsocketConnection(address=address)
app = App(
    name="test",
    group="test",
    version="0.0.1",
)
client = OmuClient(app, connection=connection)
chat = client.extensions.get(ChatExtensionType)


@client.connection.add_listener
@instance
class MyListener(ConnectionListener):
    async def on_connected(self) -> None:
        print("Connected")

    async def on_disconnected(self) -> None:
        print("Disconnected")

    async def on_event(self, event: dict) -> None:
        print(event)


@client.events.add_listener(Ready)
async def on_ready(_) -> None:
    print("Ready")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(client.start())
    loop.run_forever()
