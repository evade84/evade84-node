from operator import xor
from typing import Any, NoReturn

from node import exceptions

# def validate_slicing(first: int | None = None, last: int | None = None) -> NoReturn | None:
#     if not xor(first is not None, last is not None):
#         raise exceptions.IncorrectInputException(
#             "One of the following parameters must be specified (not both): first, last."
#         )
#     if first and first <= 0:
#         raise exceptions.IncorrectInputException("first must be more than 0.")
#     elif last and last <= 0:
#         raise exceptions.IncorrectInputException("last must be more than 0.")
