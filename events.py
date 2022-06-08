import json
from datetime import datetime
from time import time
from dataclasses import dataclass, asdict, field


def parse_json(data):
    data = json.loads(data)
    if data["type"] == "message":
        return Message(data["username"], data["content"])
    elif data["type"] == "user_join":
        return UserJoin(data["username"])
    elif data["type"] == "user_left":
        return UserLeft(data["username"])
    else:
        raise AttributeError


@dataclass(kw_only=True)
class SocketEvent:
    timestamp: float = field(default_factory=time)

    def as_json(self):
        return json.dumps(asdict(self))

    def pretty_timestamp(self):
        return datetime.fromtimestamp(self.timestamp).strftime("%H:%M")


@dataclass
class Message(SocketEvent):
    username: str
    content: str
    type: str = "message"


@dataclass
class UserJoin(SocketEvent):
    username: str
    type: str = "user_join"


@dataclass
class UserLeft(SocketEvent):
    username: str
    type: str = "user_left"
