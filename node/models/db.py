from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from beanie import Document, Link
from node import auth
from node.enums import PoolType
from pydantic import BaseModel, Field, validator
from shortuuid import ShortUUID


def short_uuid_factory():
    return ShortUUID().random(length=5)


class Signature(Document):
    uuid: str = Field(default_factory=short_uuid_factory)  # todo
    key_hash: str = Field()

    # mutable meta data
    description: str = Field(default=None)

    # immutable meta data
    value: str = Field()
    created_at: datetime = Field(default=None)

    class Collection:
        name = "signatures"

    @classmethod
    def from_request(cls, signature):
        return cls(
            key_hash=auth.hash_key(signature.key),
            value=signature.value,
            description=signature.description,
            created_at=datetime.now(),
        )


class Message(BaseModel):
    id: int
    date: datetime
    plaintext: str | None = None

    AES_encrypted: bool = False
    AES_ciphertext: bytes | None = None
    AES_nonce: bytes | None = None
    AES_tag: bytes | None = None

    signature: Link[Signature] | None = None


class Pool(Document):
    type: PoolType
    uuid: UUID = Field(default_factory=uuid4)

    # identifiers
    address: str = None
    tag: str = Field(default=None)

    # mutable meta data
    description: str = Field(default=None)
    public: bool = Field(default=False)

    # immutable meta data
    creator_signature: Link[Signature] = Field(default=None)
    created_at: datetime = Field(default=None)

    # access keys
    master_key_hash: str = Field()
    writer_key_hash: str = Field(default=None)
    reader_key_hash: str = Field(default=None)

    # encryption settings (only pools with type `tunnel` can be encrypted)
    AES_encrypted: bool = Field(default=False)

    messages: list[Message] = []

    class Collection:
        name = "pools"

    @validator("address", always=True)
    def set_address(cls, _, values: dict[str, Any]):  # noqa
        return values["uuid"].hex

    @classmethod
    async def from_request(cls, pool_type: PoolType, pool, creator_signature: Link[Signature] | None):
        master_key_hash = auth.hash_key(pool.master_key)
        writer_key_hash = auth.hash_key(pool.writer_key) if pool.writer_key else None
        reader_key_hash = auth.hash_key(pool.reader_key) if pool.reader_key else None

        return cls(
            type=pool_type,
            tag=pool.tag,
            description=pool.description,
            public=pool.public,
            creator_signature=creator_signature,
            created_at=datetime.now(),
            master_key_hash=master_key_hash,
            writer_key_hash=writer_key_hash,
            reader_key_hash=reader_key_hash,
            AES_encrypted=pool.AES_encrypted,
            messages=[],
        )
