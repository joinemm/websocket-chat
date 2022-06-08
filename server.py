import asyncio

from websockets.server import serve, WebSocketServerProtocol
from websockets.exceptions import ConnectionClosed
import json

import events

clients = set()
users = set()


async def send(websocket, message):
    try:
        await websocket.send(message)
        print("SEND >>>", message)
    except ConnectionClosed:
        pass


def broadcast(message: events.SocketEvent):
    for websocket in clients:
        asyncio.create_task(send(websocket, message.as_json()))


async def handler(websocket: WebSocketServerProtocol):
    clients.add(websocket)
    try:
        async for message in websocket:
            print("RECV <<<", message)
            data = json.loads(message)
            if data["type"] == "message":
                username = data["username"]
                content = data["content"]
                broadcast(events.Message(username, content))

            elif data["type"] == "user_join":
                username = data["username"]
                broadcast(events.UserJoin(username))
                users.add(username)
    finally:
        clients.remove(websocket)
        users.remove(username)
        broadcast(events.UserLeft(username))


async def main():
    async with serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
