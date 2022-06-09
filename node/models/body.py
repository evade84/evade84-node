from typing import Optional

from pydantic import BaseModel


class NewPool(BaseModel):
    tag: Optional[str] = None

    creator: Optional[str] = None
    description: Optional[str] = None

    master_key: Optional[str] = None
    reader_key: Optional[str] = None

    indexable: Optional[bool] = None
