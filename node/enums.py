from enum import Enum


class PoolType(str, Enum):
    wall = "wall"
    channel = "channel"
    chat = "chat"
    mailbox = "mailbox"
