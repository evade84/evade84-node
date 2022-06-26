from enum import Enum


class PoolType(str, Enum):
    wall = "wall"
    channel = "channel"
    tunnel = "tunnel"
    mailbox = "mailbox"
