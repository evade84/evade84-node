from pydantic import BaseModel


class NewPool(BaseModel):
    tag: str | None = None

    creator: str | None = None
    description: str | None = None

    master_key: str | None = None
    reader_key: str | None = None

    indexable: bool | None = None
