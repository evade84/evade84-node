from datetime import datetime
from typing import Any

from node.enums import PoolType
from pydantic import BaseModel


class Error(BaseModel):
    error_message: str


class RequestValidationErrorResponse(Error):
    detail: list[dict[str, Any]]


class Signature(BaseModel):
    uuid: str
    value: str
    description: str | None
    created_at: datetime

    @classmethod
    def from_db(cls, signature):
        return cls(
            uuid=signature.uuid,
            value=signature.value,
            description=signature.description,
            created_at=signature.created_at,
        )


class Pool(BaseModel):
    type: PoolType

    # identifiers
    address: str
    tag: str | None

    # meta data
    description: str | None
    created_at: datetime
    creator_signature: Signature | None
    public: bool
    AES_encrypted: bool

    @classmethod
    def from_db(cls, pool):
        signature = Signature.from_db(pool.creator_signature) if pool.creator_signature else None
        return cls(
            type=pool.type,
            address=pool.address,
            tag=pool.tag,
            description=pool.description,
            public=pool.public,
            created_at=pool.created_at,
            creator_signature=signature,
            AES_encrypted=pool.AES_encrypted,
        )


class Message(BaseModel):
    id: int
    date: datetime
    plaintext: str | None

    AES_encrypted: bool
    AES_ciphertext: bytes | None
    AES_nonce: bytes | None
    AES_tag: bytes | None

    signature: Signature | None

    @classmethod
    def from_db(cls, message):
        return cls(
            id=message.id,
            date=message.date,
            plaintext=message.plaintext,
            AES_encrypted=message.AES_encrypted,
            AES_ciphertext=message.ciphertext,
            AES_nonce=message.nonce,
            AES_tag=message.tag,
            signature=Signature.from_db(message.signature),
        )


class Messages(BaseModel):
    AES_encrypted: bool
    total: int
    count: int
    messages: list[Message]


class Node(BaseModel):
    name: str
    version: str
