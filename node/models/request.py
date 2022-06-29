from pydantic import BaseModel, Field, root_validator

from node.enums import PoolType


def KeyField(*, optional: bool = False):  # noqa
    if optional:
        return Field(default=None, min_length=4, max_length=128)
    else:
        return Field(min_length=4, max_length=128)


def DescriptionField():  # noqa
    return Field(default=None, min_length=1, max_length=1000)


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


class RequestNewPool(BaseModel):
    tag: str | None = Field(default=None)
    description: str | None = DescriptionField()
    public: bool = Field(default=False)
    creator_signature: RequestSignature | None = Field(default=None)

    master_key: str = KeyField()
    writer_key: str | None = KeyField(optional=True)
    reader_key: str | None = KeyField(optional=True)

    encrypted: bool = Field(default=False)

    def validate_fields(self, pool_type: PoolType) -> bool:  # todo: use root validator instead (?)
        match pool_type:
            case PoolType.wall:
                return bool(
                    not self.writer_key
                    and not self.reader_key
                    and not self.writer_key
                    and not self.encrypted
                )
            case PoolType.channel:
                return bool(not self.reader_key and self.writer_key and not self.encrypted)
            case PoolType.chat:
                return bool(self.writer_key and self.reader_key and self.encrypted is not None)
            case PoolType.mailbox:
                return bool(not self.writer_key and self.reader_key and not self.encrypted)
            case _:
                raise ValueError()


class RequestNewMessage(BaseModel):
    signature: RequestSignature | None = None


class RequestNewPlaintextMessage(RequestNewMessage):
    plaintext: str = Field(min_length=1, max_length=10000)


class RequestNewEncryptedMessage(RequestNewMessage):
    AES_ciphertext: bytes = Field(min_length=1)
    AES_nonce: bytes = Field(min_length=1)
    AES_tag: bytes = Field(min_length=1)


    # @staticmethod
    # def _validate_all_fields(
    #     plaintext: str | None = None,
    #     AES_ciphertext: bytes | None = None,
    #     AES_nonce: bytes | None = None,
    #     AES_tag: bytes | None = None,
    # ):
    #     if plaintext and not (AES_ciphertext or AES_nonce or AES_tag):
    #         return
    #     elif (not plaintext) and (AES_ciphertext and AES_nonce and AES_tag):
    #         return
    #     else:
    #         raise ValueError(
    #             "Single plaintext / AES_ciphertext, AES_nonce and AES_tag (at once) must be set."
    #         )
    #
    # @root_validator
    # def validate_all_fields(cls, values):  # noqa
    #     cls._validate_all_fields(
    #         values.get("plaintext"),
    #         values.get("AES_ciphertext"),
    #         values.get("AES_nonce"),
    #         values.get("AES_tag"),
    #     )
    #     return values
#