import asyncio
import events

from concurrent.futures import ThreadPoolExecutor
from websockets.client import connect, WebSocketClientProtocol
from websockets.exceptions import ConnectionClosed, ConnectionClosedError


async def async_input(prompt: str = ""):
    with ThreadPoolExecutor(1, "ainput") as executor:
        return (await asyncio.get_event_loop().run_in_executor(executor, input, prompt)).rstrip()


async def sender(websocket: WebSocketClientProtocol, username):
    await websocket.send(events.UserJoin(username).as_json())
    while True:
        try:
            message = ""
            while not message:
                message = await async_input()
        except KeyboardInterrupt:
            return
        await websocket.send(events.Message(username, message).as_json())


async def receiver(websocket: WebSocketClientProtocol):
    try:
        async for message in websocket:
            event = events.parse_json(message)
            if isinstance(event, events.Message):
                print(f"{event.pretty_timestamp()} | {event.username}: {event.content}")

            elif isinstance(event, events.UserJoin):
                print(f"{event.pretty_timestamp()} | --- {event.username} joined the room ---")

            elif isinstance(event, events.UserLeft):
                print(f"{event.pretty_timestamp()} | --- {event.username} left the room ---")

    except ConnectionClosedError:
        print("[server disconnected]")
        return


async def main():
    username = input("username: ")
    print("[connecting to server...]")
    try:
        async with connect("ws://localhost:8001") as websocket:
            print("[online]")
            consumer_task = asyncio.create_task(receiver(websocket))
            producer_task = asyncio.create_task(sender(websocket, username))
            _, pending = await asyncio.wait(
                [consumer_task, producer_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()

    except (ConnectionClosed, ConnectionClosedError, OSError):
        print("[server disconnected]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
