import re
from uuid import UUID, uuid4

from beanie import Document
from pydantic import BaseModel, Field, validator


class Message(BaseModel):
    index: int
    text: str
    signature: str | None = None


class Pool(Document):
    uuid: UUID = Field(default_factory=uuid4)
    address: str | None = None

    tag: str | None = None

    creator: str | None = None
    description: str | None = None

    master_key_hash: str | None = None
    reader_key_hash: str | None = None

    indexable: bool | None = None

    messages: list[Message] = []

    class Collection:
        name = "pools"

    @staticmethod
    def validate_optional_using_regex(value: str | None, pattern: str):
        if value:
            if not re.fullmatch(pattern, value):
                raise ValueError(f"does not match {pattern} regex pattern")
        return value

    @validator("address", always=True)  # todo: set pool address another way
    def set_address(cls, address: str | None, values):  # noqa
        return values["uuid"].hex

    @validator("tag")
    def validate_tag(cls, tag: str | None):  # noqa
        return cls.validate_optional_using_regex(tag, r"[a-zA-Z\d\-]{3,50}")

    @validator("creator")
    def validate_author(cls, creator: str | None):  # noqa
        return cls.validate_optional_using_regex(creator, r".{1,40}")  # todo

    @validator("description")
    def validate_description(cls, description: str | None):  # noqa
        return cls.validate_optional_using_regex(description, r".{1,500}")  # todo

    @validator("indexable")
    def validate_indexable(cls, indexable: bool | None):  # noqa
        return bool(indexable)
