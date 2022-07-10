from enum import Enum


class MessageType(str, Enum):
    plaintext = "plaintext"
    encrypted = "encrypted"


class PoolType(str, Enum):
    wall = "wall"
    channel = "channel"
    chat = "chat"
    mailbox = "mailbox"
