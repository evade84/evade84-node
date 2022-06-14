from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from beanie import Document, Link
from pydantic import BaseModel, Field, validator


class Signature(Document):
    tag: str
    key_hash: str

    # mutable meta data
    description: str = None

    # immutable meta data
    creation_date: datetime = None

    class Collection:
        name = "signatures"

    def __str__(self):
        return f"Signature({self.tag})"


class Message(BaseModel):
    id: int
    text: str
    signature: Optional[Link[Signature]] = None

    def __str__(self):
        signature = self.signature or "<no signature>"
        return f"Message({self.text} from={signature})"


class Pool(Document):
    uuid: UUID = Field(default_factory=uuid4)

    # identifiers
    address: str = None
    tag: str = None

    # mutable meta data
    public: bool = False
    description: str = None

    # immutable meta data
    creator_signature: Signature = None
    creation_date: datetime = None

    # access keys
    master_key_hash: str
    writer_key_hash: str = None
    reader_key_hash: str = None

    messages: list[Message] = []

    class Collection:
        name = "pools"

    def __str__(self):
        write = "key_owner" if self.writer_key_hash else "anyone"
        read = "key_owner" if self.reader_key_hash else "anyone"
        return f"Pool({self.tag if self.tag else '<no tag>'}, {self.address}, read={read}, write={write})"

    @validator("address", always=True)
    def set_address(cls, address: str | None, values):  # noqa
        return values["uuid"].hex
