from typing import Any, NoReturn, Type

from node import auth, exceptions, models

from node.exceptions import APIException


def generate_responses(
    success_description: str, api_exceptions: list[Type[APIException]]
) -> dict[int, dict[str, Any]]:
    responses = {
        200: {"description": f"**Successful response:**\n\n{success_description}"},
        422: {
            "description": "**Unprocessable entity.**",
            "model": models.response.ResponseError,
        },
    }
    for exception in api_exceptions:
        responses[exception.status_code] = {
            "description": f"**{exception.error_message}**",
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
        raise exceptions.InvalidSignatureKeyException("Invalid signature key.")
    return db_signature


def build_errors_message(prefix: str, errors: list[str]):
    return f"{prefix}: {', '.join(errors)}."
