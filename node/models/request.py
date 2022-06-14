from operator import xor

from node.exceptions import IncorrectInputException
from pydantic import BaseModel, Field

_SIGNATURE_TAG_REGEX = r"[\w\s-]{1,35}"

_KEY_MIN_LENGTH = 8
_KEY_MAX_LENGTH = 128

_DESCRIPTION_MAX_LENGTH = 500


def validate_signature_fields(signature_tag: str | None, signature_key: str | None) -> bool:
    if xor(bool(signature_tag), bool(signature_key)):
        return False
    return True


class RequestMessage(BaseModel):
    text: str = Field(min_length=1, max_length=10000)
    writer_key: str | None = Field(default=None, min_length=_KEY_MIN_LENGTH, max_length=_KEY_MAX_LENGTH)
    signature_tag: str | None = Field(default=None, regex=_SIGNATURE_TAG_REGEX)
    signature_key: str | None = Field(default=None, min_length=_KEY_MIN_LENGTH, max_length=_KEY_MAX_LENGTH)
    hide_message_date: bool = Field(default=False)

    def validate_message_signature_fields(self):
        if not validate_signature_fields(self.signature_tag, self.signature_key):
            raise IncorrectInputException("signature_tag and signature_key must be specified in pair.")


class RequestPool(BaseModel):
    tag: str | None = Field(default=None, regex=r"[\w-]{1,500}")
    description: str | None = Field(default=None, min_length=1, max_length=_DESCRIPTION_MAX_LENGTH)

    creator_signature_tag: str | None = Field(default=None, regex=_SIGNATURE_TAG_REGEX)
    creator_signature_key: str | None = Field(default=None, min_length=_KEY_MIN_LENGTH, max_length=_KEY_MAX_LENGTH)

    master_key: str = Field(min_length=_KEY_MIN_LENGTH, max_length=_KEY_MAX_LENGTH)
    writer_key: str | None = Field(default=None, min_length=_KEY_MIN_LENGTH, max_length=_KEY_MAX_LENGTH)
    reader_key: str | None = Field(default=None, min_length=_KEY_MIN_LENGTH, max_length=_KEY_MAX_LENGTH)

    public: bool = Field(default=False)
    hide_creation_date: bool = Field(default=False)

    class Config:
        schema_extra = {
            "example": {
                "tag": "food-blog",
                "description": "This is my blog. Here I log everything I ate!",
                "creator_signature_tag": "Elon Musk",
                "creator_signature_key": "very-strong-password",
                "master_key": "the-most-strongest-password-i-have-ever-seen",
                "writer_key": "qwerty12345",
                "reader_key": "anyone-can-guess",
                "public": True,
                "hide_creation_date": False,
            }
        }

    def validate_creator_signature_fields(self):
        if not validate_signature_fields(self.creator_signature_tag, self.creator_signature_key):
            raise IncorrectInputException("Creator signature tag and creator signature key must be both specified.")


class RequestEditPool(RequestPool):
    master_key: str | None = Field(default=None, min_length=_KEY_MIN_LENGTH, max_length=_KEY_MAX_LENGTH)


class RequestSignature(BaseModel):
    tag: str = Field(regex=_SIGNATURE_TAG_REGEX)
    key: str = Field(min_length=_KEY_MIN_LENGTH, max_length=_KEY_MAX_LENGTH)
    description: str | None = Field(min_length=1, max_length=_DESCRIPTION_MAX_LENGTH)
    hide_creation_date: bool = Field(default=False)

    class Config:
        schema_extra = {
            "example": {
                "tag": "Elon Musk",
                "key": "very-strong-password",
                "description": "Official signature that belongs to Elon Musk.",
                "hide_creation_date": False,
            }
        }
