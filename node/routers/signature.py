from datetime import datetime

from fastapi import APIRouter
from loguru import logger
from node import auth, crud, exceptions, models, util

router = APIRouter(prefix="/signature")


@router.get(
    "/{tag}",
    name="Get information about given signature",
    description="Returns requested signature.",
    responses=util.generate_responses("Returns signature object.", []),
    response_model=models.response.ResponseSignature,
)
async def get_signature(tag: str):
    signature = await crud.get_signature(tag)
    if not signature:
        raise exceptions.SignatureDoesNotExistException()
    return models.response.ResponseSignature.from_db_signature(signature)


@router.post(
    "/new",
    name="Create a new signature",
    description="Creates a new unique signature.",
    responses=util.generate_responses(
        "Returns newly created signature object.",
        [
            exceptions.ConflictException,
        ],
    ),
    response_model=models.response.ResponseSignature,
)
async def create_signature(signature: models.request.RequestSignature):
    if await crud.signature_exists(signature.tag):
        raise exceptions.ConflictException("Signature already exists.")
    db_signature = models.db.Signature(
        tag=signature.tag,
        description=signature.description,
        key_hash=auth.hash_key(signature.key),
        creation_date=None if signature.hide_creation_date else datetime.now(),
    )
    await db_signature.save()
    logger.info(f"Created new signature: {db_signature.tag}")
    return models.response.ResponseSignature.from_db_signature(db_signature)
