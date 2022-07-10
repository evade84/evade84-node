from typing import Any

from pydantic import BaseModel, Extra, Field, ValidationError, root_validator, validator

from node.enums import MessageType, PoolType


def KeyField(*, optional: bool = False):  # noqa
    if optional:
        return Field(default=None, min_length=4, max_length=128)
    else:
        return Field(min_length=4, max_length=128)


def DescriptionField():  # noqa
    return Field(default=None, min_length=1, max_length=1000)


def TagField():  # noqa
    return Field(default=None, regex=r".+")


class RequestUpdateSignature(BaseModel):
    new_description: str | None = DescriptionField()
    new_key: str | None = KeyField(optional=True)
    new_value: str | None = Field(default=None, min_length=1, max_length=50)


class RequestSignature(BaseModel):
    uuid: str = Field()
    key: str = KeyField()


# class RequestUpdateSignature(BaseModel):
#     key: str = Field()
#     new_key: str | None = key_field(optional=True)
#     description: str | None = description_field()


class RequestNewSignature(BaseModel):
    value: str = Field()
    key: str = KeyField()
    description: str | None = DescriptionField()


class RequestUpdatePool(BaseModel):
    new_description: str | None = DescriptionField()

    new_master_key: str | None = KeyField(optional=True)
    new_writer_key: str | None = KeyField(optional=True)
    new_reader_key: str | None = KeyField(optional=True)


class RequestNewPool(BaseModel, extra=Extra.forbid):
    tag: str | None = TagField()
    description: str | None = DescriptionField()

    public: bool = Field(default=False)
    encrypted: bool = Field(default=False)

    creator_signature: RequestSignature | None = Field(default=None)

    master_key: str = KeyField()
    writer_key: str = KeyField(optional=True)
    reader_key: str = KeyField(optional=True)

    def validate_based_on_type(self, pool_type: PoolType) -> list[str]:
        """Returns list of errors detected. (Empty list if not errors)"""
        errors = []
        match pool_type:
            case PoolType.wall:
                if self.writer_key:
                    errors.append("pool with type wall must not have writer key")
                if self.reader_key:
                    errors.append("pool with type wall must not have reader key")
            case PoolType.channel:
                if not self.writer_key:
                    errors.append("pool with type channel must have writer key")
                if self.reader_key:
                    errors.append("pool with type channel must not have reader key")
            case PoolType.chat:
                if not self.writer_key:
                    errors.append("pool with type chat must have writer key")
                if not self.reader_key:
                    errors.append("pool with type chat must have reader key")
            case PoolType.mailbox:
                if self.writer_key:
                    errors.append("pool with type mailbox must not have writer key")
                if not self.reader_key:
                    errors.append("pool with type mailbox must have reader key")
            case _:
                raise ValueError("Invalid pool type.")

        if pool_type != PoolType.chat and self.encrypted is True:
            errors.append(
                f"pool with type {pool_type} can't be encrypted (only pools with type chat can be encrypted)"
            )
        return errors


class RequestNewMessage(BaseModel, extra=Extra.forbid):
    signature: RequestSignature | None = Field(default=None)

    plaintext: str | None = Field(default=None, min_length=1, max_length=10000)

    AES_ciphertext: bytes | None = Field(default=None, min_length=1)
    AES_nonce: bytes | None = Field(default=None, min_length=1)
    AES_tag: bytes | None = Field(default=None, min_length=1)

    def validate_based_on_type(self, message_type: MessageType) -> list[str]:
        errors = []
        match message_type:
            case MessageType.plaintext:
                if not self.plaintext:
                    errors.append("plaintext message must have plaintext field.")
                if self.AES_ciphertext:
                    errors.append("plaintext message must not have AES_ciphertext field.")
                if self.AES_nonce:
                    errors.append("plaintext message must not have AES_nonce field.")
                if self.AES_tag:
                    errors.append("plaintext message must not have AES_tag field.")

            case MessageType.encrypted:
                if self.plaintext:
                    errors.append("encrypted message must not have plaintext field.")
                if not self.AES_ciphertext:
                    errors.append("encrypted message must have AES_ciphertext field.")
                if not self.AES_nonce:
                    errors.append("encrypted message must have AES_nonce field.")
                if not self.AES_tag:
                    errors.append("encrypted message must have AES_tag field.")

            case _:
                raise ValueError("Invalid message type.")

        return errors
