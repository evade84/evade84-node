from operator import xor
from typing import Any, NoReturn

from node import exceptions


def validate_first_last_params(first: int | None = None, last: int | None = None) -> NoReturn | None:
    if not xor(first is not None, last is not None):
        raise exceptions.UnprocessableEntityException(
            "One of the following parameters must be specified (not both): `first`, `last`."
        )
    if first and first <= 0:
        raise exceptions.UnprocessableEntityException("`first` must be more than 0.")
    elif last and last <= 0:
        raise exceptions.UnprocessableEntityException("`last` must be more than 0.")


def validate_limit_offset_params(limit: int, offset: int) -> NoReturn | None:
    if limit <= 0:
        raise exceptions.UnprocessableEntityException("`limit` must be more than 0.")
    if offset < 0:
        raise exceptions.UnprocessableEntityException("`offset` must be more than 0 or equal to it.")


def paginate_first_last(x: list[Any], first: int = None, last: int | None = None) -> list[Any]:
    if first:
        return x[:first]
    elif last:
        return x[::-1][:last][::-1]
    else:
        raise ValueError()


def paginate_limit_offset(x, limit: int, offset: int) -> list[Any]:
    return x[offset : offset + limit]
