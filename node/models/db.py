import re
from typing import Optional
from uuid import UUID, uuid4

from beanie import Document
from pydantic import BaseModel, Field, validator


class Message(BaseModel):
    index: int
    text: str
    signature: str | None = None


class Pool(Document):
    uuid: UUID = Field(default_factory=uuid4)
    address: Optional[str] = None

    tag: Optional[str] = None

    creator: Optional[str] = None
    description: Optional[str] = None

    master_key_hash: Optional[str] = None
    reader_key_hash: Optional[str] = None

    indexable: Optional[bool] = None

    messages: list[Message] = []

    class Collection:
        name = "pools"

    @staticmethod
    def validate_optional_using_regex(value: Optional[str], pattern: str):
        if value:
            if not re.fullmatch(pattern, value):
                raise ValueError(f"does not match {pattern} regex pattern")
        return value

    @validator("address", always=True)  # todo: do something more
    def set_address(cls, address: str | None, values):  # noqa
        return values["uuid"].hex

    @validator("tag")
    def validate_tag(cls, tag: Optional[str]):  # noqa
        return cls.validate_optional_using_regex(tag, r"[a-zA-Z\d\-]{3,50}")

    @validator("creator")
    def validate_author(cls, creator: Optional[str]):  # noqa
        return cls.validate_optional_using_regex(creator, r".+")

    @validator("description")
    def validate_description(cls, description: Optional[str]):  # noqa
        return cls.validate_optional_using_regex(description, r".+")

    @validator("indexable")
    def validate_indexable(cls, indexable: Optional[bool]):  # noqa
        return bool(indexable)
