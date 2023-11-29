import asyncio

from omu.connection.address import Address
from omu.helper import instance
from omuserver.extension.table import TableExtensionServer
from omuserver.fastapi_server import FastApiServer
from omuserver.network.network import NetworkListener
from omuserver.session.session import Session

server = FastApiServer(
    Address(
        host="0.0.0.0",
        port=26423,
        secure=False,
    )
)
server.extensions["table"] = TableExtensionServer(server)


@server.network.add_listener
@instance
class MyListener(NetworkListener):
    async def on_connected(self, session: Session) -> None:
        print(f"Connected: {session.app.name}")

    async def on_disconnected(self, session: Session) -> None:
        print(f"Disconnected: {session.app.name}")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(server.start())
    loop.run_forever()
