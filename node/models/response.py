from datetime import datetime

from node.models import db
from pydantic import BaseModel


class ResponseError(BaseModel):
    error_message: str


class ResponseSignature(BaseModel):
    tag: str
    description: str = None
    creation_date: datetime = None

    @classmethod
    def from_db_signature(cls, signature: db.Signature):
        return cls(
            tag=signature.tag,
            description=signature.description,
            creation_date=signature.creation_date,
        )


class ResponsePool(BaseModel):
    # identifiers
    address: str
    tag: str = None

    # meta data
    public: bool

    description: str = None
    creation_date: datetime = None
    creator_signature: ResponseSignature = None

    write_key_required: bool
    read_key_required: bool

    @classmethod
    def from_db_pool(cls, pool: db.Pool):
        return cls(
            address=pool.address,
            tag=pool.tag,
            public=pool.public,
            description=pool.description,
            creation_date=pool.creation_date,
            creator_signature=pool.creator_signature,
            write_key_required=bool(pool.writer_key_hash),
            read_key_required=bool(pool.reader_key_hash),
        )


class ResponseMessage(BaseModel):
    id: int
    text: str
    signature: ResponseSignature = None

    @classmethod
    def from_db_message(cls, message: db.Message):
        return cls(
            id=message.id,
            text=message.text,
            signature=ResponseSignature.from_db_signature(message.signature),
        )


class ResponseMessages(BaseModel):
    total: int
    count: int
    messages: list[ResponseMessage]

    @classmethod
    def from_messages(cls, total: int, messages: list[db.Message]):
        return cls(
            total=total,
            count=len(messages),
            messages=[ResponseMessage.from_db_message(message) for message in messages],
        )


class ResponsePools(BaseModel):
    total: int
    count: int
    pools: list[ResponsePool]

    @classmethod
    def from_pools(cls, total: int, pools: list[db.Pool]):
        return cls(
            total=total,
            count=len(pools),
            pools=[ResponsePool.from_db_pool(pool) for pool in pools],
        )


class ResponseNode(BaseModel):
    name: str
    version: str
