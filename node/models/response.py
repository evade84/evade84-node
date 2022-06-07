from pydantic import BaseModel

from node.models import db


class Error(BaseModel):
    error_message: str


class Pool(BaseModel):
    address: str
    tag: str | None = None
    creator: str | None = None
    description: str | None = None
    indexable: bool


class Messages(BaseModel):
    total: int
    messages: list[db.Message]


class Pools(BaseModel):
    total: int
    pools: list[Pool]


class Node(BaseModel):
    version: str
    indexable_pools_count: int
