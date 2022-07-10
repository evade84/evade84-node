from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from beanie import Document, Link
from pydantic import BaseModel, Field, validator
from shortuuid import ShortUUID

from node import auth, models
from node.enums import MessageType, PoolType


def short_uuid_factory():
    return ShortUUID().random(length=5)


class Signature(Document):
    uuid: str = Field(default_factory=short_uuid_factory)
    key_hash: str

    # mutable meta data
    description: str | None

    # immutable meta data
    value: str
    created_at: datetime

    class Collection:
        name = "signatures"

    def __str__(self):
        return f"Signature({self.value}, uuid={self.uuid})"

    @classmethod
    def from_request(cls, signature):
        return cls(
            key_hash=auth.hash_key(signature.key),
            value=signature.value,
            description=signature.description,
            created_at=datetime.now(),
        )


class Message(BaseModel):
    type: MessageType
    id: int
    date: datetime
    signature: Link[Signature] | None


class PlaintextMessage(Message):
    plaintext: str

    def __str__(self):
        return f'PlaintextMessage("{self.plaintext}" by={self.signature})'


class EncryptedMessage(Message):
    AES_ciphertext: bytes
    AES_nonce: bytes
    AES_tag: bytes

    def __str__(self):
        return f"EncryptedMessage({len(self.AES_ciphertext)} chars by={self.signature})"


class Pool(Document):
    type: PoolType
    uuid: UUID = Field(default_factory=uuid4)

    # identifiers
    address: str = None
    tag: str | None

    # mutable meta data
    description: str | None
    public: bool

    # immutable meta data
    creator_signature: Link[Signature] | None
    created_at: datetime

    # access keys
    master_key_hash: str = Field()
    writer_key_hash: str | None
    reader_key_hash: str | None

    # encryption settings (only pools with type `chat` can be encrypted)
    encrypted: bool

    messages: list[PlaintextMessage | EncryptedMessage] = []

    class Collection:
        name = "pools"

    def __str__(self):
        return f"Pool_{self.type}({self.tag} ({self.address}) creator={self.creator_signature} public={self.public})"

    @validator("address", always=True)
    def set_address(cls, _, values: dict[str, Any]):  # noqa
        return values["uuid"].hex

    @classmethod
    def from_request_model(cls, pool_type: PoolType, pool, creator_signature: Signature | None):
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
            encrypted=pool.encrypted,
            messages=[],
        )
