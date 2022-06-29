from datetime import datetime
from typing import Any, Optional

from beanie import Link
from pydantic import BaseModel

from node.enums import PoolType
from node.models import db


class ResponseError(BaseModel):
    error_message: str


class ResponseRequestValidationError(ResponseError):
    detail: list[dict[str, Any]]


class ResponseSignature(BaseModel):
    uuid: str
    value: str
    description: str | None
    created_at: datetime

    @classmethod
    async def from_link(cls, signature: Link[db.Signature]):
        signature = await signature.fetch()
        return cls.from_db_model(signature)

    @classmethod
    def from_db_model(cls, signature: db.Signature):
        return cls(
            uuid=signature.uuid,
            value=signature.value,
            description=signature.description,
            created_at=signature.created_at,
        )


class ResponsePool(BaseModel):
    type: PoolType

    tag: str | None
    address: str
    encrypted: bool

    public: bool
    description: str | None = None

    created_at: datetime
    creator_signature: Optional[ResponseSignature]

    @classmethod
    def from_db_model(cls, pool: db.Pool):
        pool.creator_signature: db.Signature
        if pool.creator_signature:
            signature = ResponseSignature.from_db_model(pool.creator_signature)
        else:
            signature = None
        return cls(
            type=pool.type,
            address=pool.address,
            tag=pool.tag,
            description=pool.description,
            public=pool.public,
            created_at=pool.created_at,
            creator_signature=signature,
            encrypted=pool.encrypted,
        )


class ResponsePools(BaseModel):
    total: int
    count: int
    pools: list[ResponsePool]


class ResponseMessage(BaseModel):
    id: int
    date: datetime
    plaintext: str | None

    AES_ciphertext: bytes | None
    AES_nonce: bytes | None
    AES_tag: bytes | None

    signature: ResponseSignature | None

    @classmethod
    async def from_db_model(cls, message: db.Message):
        signature = await ResponseSignature.from_link(message.signature)
        return cls(
            id=message.id,
            date=message.date,
            plaintext=message.plaintext,
            AES_ciphertext=message.AES_ciphertext,
            AES_nonce=message.AES_nonce,
            AES_tag=message.AES_tag,
            signature=signature,
        )


class ResponseMessages(BaseModel):
    total: int
    count: int
    encrypted: bool
    messages: list[ResponseMessage]


class ResponseNode(BaseModel):
    name: str
    version: str
    pools_count: int
