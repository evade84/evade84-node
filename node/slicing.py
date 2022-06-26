from operator import xor
from typing import Any, NoReturn

from node import exceptions


def validate_params(first: int | None = None, last: int | None = None) -> NoReturn | None:
    if not xor(first is not None, last is not None):
        raise exceptions.IncorrectInputException(
            "One of the following parameters must be specified (not both): `first`, `last`."
        )
    if first and first <= 0:
        raise exceptions.IncorrectInputException("`first` parameter must be more than 0")
    elif last and last <= 0:
        raise exceptions.IncorrectInputException("`last` parameter must be more than 0")


def slice_list(x: list[Any], first: int = None, last: int | None = None) -> list[Any]:
    if first:
        return x[:first]
    elif last:
        return x[::-1][:last][::-1]
    else:
        raise RuntimeError()
