from pydantic import BaseModel

from node.models import db


class ResponseError(BaseModel):
    error_message: str


class ResponsePool(BaseModel):
    address: str
    tag: str | None = None
    description: str | None = None
    creator: str | None = None
    write_key_required: bool
    read_key_required: bool
    indexable: bool

    @classmethod
    def from_pool(cls, pool: db.Pool):
        return cls(
            address=pool.address,
            tag=pool.tag,
            description=pool.description,
            creator=pool.creator,
            write_key_required=bool(pool.master_key_hash),
            read_key_required=bool(pool.reader_key_hash),
            indexable=pool.indexable,
        )


class ResponseMessages(BaseModel):
    total: int
    messages: list[db.Message]

    @classmethod
    def from_messages(cls, messages: list[db.Message]):
        return cls(total=len(messages), messages=messages)


class ResponsePools(BaseModel):
    total: int
    pools: list[ResponsePool]

    @classmethod
    def from_pools(cls, pools: list[db.Pool]):
        return cls(
            total=len(pools), pools=[ResponsePool.from_pool(pool) for pool in pools]
        )


class ResponseNode(BaseModel):
    name: str
    version: str
