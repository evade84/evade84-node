from node.enums import PoolType
from pydantic import BaseModel, Field, root_validator


def key_field(*, optional: bool = False):
    if optional:
        return Field(default=None, min_length=4, max_length=128)
    else:
        return Field(min_length=4, max_length=128)


def description_field():
    return Field(default=None, min_length=1, max_length=1000)


class Signature(BaseModel):
    uuid: str = Field()
    key: str = key_field()


class UpdateSignature(BaseModel):
    key: str = Field()
    new_key: str | None = key_field(optional=True)
    description: str | None = description_field()


class NewSignature(BaseModel):
    value: str = Field()
    key: str = key_field()
    description: str | None = description_field()


class NewPool(BaseModel):
    tag: str | None = Field(default=None)
    description: str | None = description_field()
    public: bool = Field(default=False)
    creator_signature: Signature | None = Field(default=None)

    master_key: str = key_field()
    writer_key: str | None = key_field(optional=True)
    reader_key: str | None = key_field(optional=True)

    AES_encrypted: bool = Field(default=False)

    def validate_fields(self, pool_type: PoolType) -> bool:
        match pool_type:
            case PoolType.wall:
                return bool(
                    not self.writer_key
                    and not self.reader_key
                    and not self.writer_key
                    and not self.AES_encrypted
                )
            case PoolType.channel:
                return bool(not self.reader_key and self.writer_key and not self.AES_encrypted)
            case PoolType.tunnel:
                return bool(self.writer_key and self.reader_key and self.AES_encrypted is not None)
            case PoolType.mailbox:
                return bool(not self.writer_key and self.reader_key and not self.AES_encrypted)
            case _:
                raise ValueError()


class NewMessage(BaseModel):
    plaintext: str | None = None

    AES_encrypted: bool = False
    AES_ciphertext: bytes | None = None
    AES_nonce: bytes | None = None
    AES_tag: bytes | None = None
    signature: Signature | None = None

    @root_validator
    def validate_all_fields(cls, values):  # noqa
        print(values)
        # todo: I suppose it should be rewritten in more simple way
        if values.get("plaintext") and not (
            values.get("AES_encrypted")
            or values.get("AES_ciphertext")
            or values.get("AES_nonce")
            or values.get("AES_tag")
        ):
            return values
        elif not values.get("plaintext") and (
            values.get("AES_encrypted")
            and values.get("AES_ciphertext")
            and values.get("AES_nonce")
            and values.get("AES_tag")
        ):
            return values
        else:
            raise ValueError("Invalid parameters for this kind of message.")
