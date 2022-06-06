from pydantic import BaseModel


class Error(BaseModel):
    error_message: str


class Pool(BaseModel):
    address: str
    indexable: bool
    tag: str | None = None
    creator: str | None = None
    description: str | None = None


class Node(BaseModel):
    version: str
    pools_count: int
