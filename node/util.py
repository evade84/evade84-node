from typing import Any, NoReturn, Type

from node import auth, exceptions, models
from node.exceptions import APIErrorException


def generate_responses(
    success_description: str, api_exceptions: list[Type[APIErrorException]]
) -> dict[int, dict[str, Any]]:
    responses = {
        200: {"description": f"**Successful response**\n\n{success_description}"},
        422: {
            "description": f"**Request validation error**",
            "model": models.response.RequestValidationErrorResponse,
        },
    }
    for exception in api_exceptions:
        responses[exception.status_code] = {
            "description": f"**{exception.description}**",
            "model": models.response.Error,
        }
    return responses


async def get_verified_signature(signature: models.request.Signature) -> NoReturn | models.db.Signature:
    db_signature = await models.db.Signature.find_one(models.db.Signature.uuid == signature.uuid)
    if not db_signature:
        raise exceptions.SignatureNotFoundException()
    if not auth.verify_key(signature.key, db_signature.key_hash):
        raise exceptions.AccessDeniedException("Invalid signature key.")
    return db_signature
