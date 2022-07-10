from typing import Any, NoReturn, Type

from node import auth, exceptions, models

# from node.enums import PoolType
from node.exceptions import APIErrorException

# from fastapi.exceptions import RequestValidationError
# from pydantic import BaseConfig, ValidationError
# from pydantic.error_wrappers import ErrorWrapper, error_dict


def generate_responses(
    success_description: str, api_exceptions: list[Type[APIErrorException]]
) -> dict[int, dict[str, Any]]:
    responses = {
        200: {"description": f"**Successful response**\n\n{success_description}"},
        422: {
            "description": "**Request validation error**",
            "model": models.response.ResponseRequestValidationError,
        },
    }
    for exception in api_exceptions:
        responses[exception.status_code] = {
            "description": f"**{exception.description}**",
            "model": models.response.ResponseError,
        }
    return responses


async def get_verified_signature(
    signature: models.request.RequestSignature,
) -> models.database.Signature | NoReturn:
    db_signature = await models.database.Signature.find_one(
        models.database.Signature.uuid == signature.uuid
    )
    if not db_signature:
        raise exceptions.SignatureNotFoundException()
    if not auth.verify_key(signature.key, db_signature.key_hash):
        raise exceptions.AccessDeniedException("Invalid signature key.")
    return db_signature


def build_errors_message(prefix: str, errors: list[str]):
    return f"{prefix}: {', '.join(errors)}."
