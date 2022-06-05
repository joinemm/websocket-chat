import asyncio
import json

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from websockets.client import connect, WebSocketClientProtocol
from websockets.exceptions import ConnectionClosed, ConnectionClosedError


async def async_input(prompt: str = ""):
    with ThreadPoolExecutor(1, "ainput") as executor:
        return (await asyncio.get_event_loop().run_in_executor(executor, input, prompt)).rstrip()


async def sender(websocket: WebSocketClientProtocol, username):
    await websocket.send(json.dumps({"type": "user_join", "username": username}))
    while True:
        try:
            message = ""
            while not message:
                message = await async_input()
        except KeyboardInterrupt:
            return
        await websocket.send(
            json.dumps({"type": "send_message", "username": username, "content": message})
        )


async def receiver(websocket: WebSocketClientProtocol):
    try:
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "receive_message":
                time = datetime.fromtimestamp(data["time"]).strftime("%H:%M")
                print(f'{time} | {data["username"]}: {data["content"]}')

            elif data["type"] == "user_join":
                time = datetime.fromtimestamp(data["time"]).strftime("%H:%M")
                print(f'{time} | --- {data["username"]} joined the room ---')

            elif data["type"] == "user_left":
                time = datetime.fromtimestamp(data["time"]).strftime("%H:%M")
                print(f'{time} | --- {data["username"]} left the room ---')

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
