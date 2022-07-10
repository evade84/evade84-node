from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

from node.enums import MessageType, PoolType
from node.models import database


class ResponseError(BaseModel):
    error_message: str


class ResponseRequestValidationError(ResponseError):
    detail: list[dict[str, Any]]


class ResponseSignature(BaseModel):
    uuid: str
    value: str
    description: str | None
    created_at: datetime

    # @classmethod
    # async def from_link(cls, signature: Link[database.Signature]):
    #     signature = await signature.fetch()
    #     return cls.from_db_model(signature)

    @classmethod
    def from_db_model(cls, signature: database.Signature):
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
    def from_db_model(cls, pool: database.Pool):
        pool.creator_signature: database.Signature  # noqa
        if pool.creator_signature:
            creator_signature = ResponseSignature.from_db_model(pool.creator_signature)
        else:
            creator_signature = None
        return cls(
            type=pool.type,
            address=pool.address,
            tag=pool.tag,
            description=pool.description,
            public=pool.public,
            created_at=pool.created_at,
            creator_signature=creator_signature,
            encrypted=pool.encrypted,
        )


class ResponsePools(BaseModel):
    total: int
    count: int
    pools: list[ResponsePool]


class _ResponseMessage(BaseModel):
    type: MessageType
    id: int
    date: datetime
    signature: ResponseSignature | None


class ResponsePlaintextMessage(_ResponseMessage):
    plaintext: str

    @classmethod
    def from_db_model(cls, message: database.PlaintextMessage):
        return cls(
            type=message.type,
            id=message.id,
            date=message.date,
            signature=message.signature,
            plaintext=message.plaintext,
        )


class ResponseEncryptedMessage(_ResponseMessage):
    AES_ciphertext: bytes
    AES_nonce: bytes
    AES_tag: bytes

    @classmethod
    def from_db_model(cls, message: database.EncryptedMessage):
        return cls(
            type=message.type,
            id=message.id,
            date=message.date,
            signature=message.signature,
            AES_ciphertext=message.AES_ciphertext,
            AES_nonce=message.AES_nonce,
            AES_tag=message.AES_tag,
        )


class ResponseMessages(BaseModel):
    total: int
    count: int
    encrypted: bool
    messages: list[ResponsePlaintextMessage | ResponseEncryptedMessage]


class ResponseNode(BaseModel):
    name: str
    description: str
    version: str
    uptime: int
    pools_count: int
    signatures_count: int
