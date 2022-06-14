from typing import Any, Type

from node.exceptions import APIErrorException
from node.models.response import ResponseError


def generate_responses(
    success_description: str, exceptions: list[Type[APIErrorException]]
) -> dict[int, dict[str, Any]]:
    responses = {200: {"description": f"**Successful response**\n\n{success_description}"}}
    for exception in exceptions:
        responses[exception.status_code] = {
            "description": f"**{exception.description}**",
            "model": ResponseError,
        }
    return responses


def slice_list(x: list[Any], first: int = None, last: int | None = None) -> list[Any]:
    if first:
        return x[:first]
    elif last:
        return x[::-1][:last][::-1]
    else:
        raise RuntimeError()
