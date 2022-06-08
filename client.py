import asyncio
import events

from aioconsole import ainput
from websockets.client import connect, WebSocketClientProtocol
from websockets.exceptions import ConnectionClosed, ConnectionClosedError


async def sender(websocket: WebSocketClientProtocol, username):
    await websocket.send(events.UserJoin(username).as_json())
    while True:
        try:
            message = ""
            while not message:
                message = await ainput()
        except KeyboardInterrupt:
            return
        await websocket.send(events.Message(username, message).as_json())


async def receiver(websocket: WebSocketClientProtocol):
    async for message in websocket:
        event = events.parse_json(message)
        if isinstance(event, events.Message):
            print(f"{event.pretty_timestamp()} | {event.username}: {event.content}")

        elif isinstance(event, events.UserJoin):
            print(f"{event.pretty_timestamp()} | --- {event.username} joined the room ---")

        elif isinstance(event, events.UserLeft):
            print(f"{event.pretty_timestamp()} | --- {event.username} left the room ---")


async def main():
    username = input("username: ")
    print("[connecting to server...]")
    try:
        async with connect("ws://localhost:8001") as websocket:
            print("[online]")
            consumer_task = asyncio.create_task(receiver(websocket))
            producer_task = asyncio.create_task(sender(websocket, username))
            await asyncio.gather(consumer_task, producer_task, return_exceptions=False)

    except (ConnectionClosed, ConnectionClosedError, OSError):
        print("[server disconnected]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
