import asyncio
from time import time

from websockets.server import serve, WebSocketServerProtocol
from websockets.exceptions import ConnectionClosed
import json

clients = set()


async def send(websocket, message):
    try:
        await websocket.send(message)
        print("SEND >>>", message)
    except ConnectionClosed:
        pass


def broadcast(message):
    for _, websocket in clients:
        asyncio.create_task(send(websocket, message))


async def handler(websocket: WebSocketServerProtocol):
    try:
        async for message in websocket:
            print("RECV <<<", message)
            data = json.loads(message)
            if data["type"] == "send_message":
                username = data["username"]
                content = data["content"]
                broadcast(
                    json.dumps(
                        {
                            "type": "receive_message",
                            "time": time(),
                            "username": username,
                            "content": content,
                        }
                    )
                )
            elif data["type"] == "user_join":
                username = data["username"]
                broadcast(json.dumps({"type": "user_join", "time": time(), "username": username}))
                clients.add((username, websocket))
    finally:
        clients.remove((username, websocket))
        broadcast(json.dumps({"type": "user_left", "time": time(), "username": username}))


async def main():
    async with serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
