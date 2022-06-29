from fastapi import APIRouter
from loguru import logger

from node import auth, crud, exceptions, models, util

router = APIRouter(prefix="/signature")


@router.post(
    "/create",
    response_model=models.response.ResponseSignature,
    summary="Create signature",
    description="Creates new signature",
    responses=util.generate_responses("Returns newly created signature", []),
)
async def create_signature(signature: models.request.RequestNewSignature):
    db_signature = models.db.Signature.from_request(signature)
    await db_signature.create()
    logger.info(f"Created new signature: {db_signature}.")
    return models.response.ResponseSignature.from_db_model(db_signature)


@router.get(
    "/{uuid}",
    response_model=models.response.ResponseSignature,
    summary="Get signature information",
    description="Returns information about signature",
    responses=util.generate_responses(
        "Returns requested signature object", [exceptions.SignatureNotFoundException]
    ),
)
async def get_signature(uuid: str):
    signature = await crud.get_signature(uuid)
    if not signature:
        raise exceptions.SignatureNotFoundException()
    return models.response.ResponseSignature.from_db_model(signature)


@router.post(
    "/{uuid}/update",
    response_model=models.response.ResponseSignature,
    summary="Update signature",
    description="Updates some signature fields",
    responses=util.generate_responses(
        "Returns updated signature object", [exceptions.AccessDeniedException]
    ),
)
async def update_signature(uuid: str, key: str, signature_data: models.request.RequestUpdateSignature):
    signature = await crud.get_signature(uuid)
    if not signature:
        raise exceptions.SignatureNotFoundException()
    if not auth.verify_key(key, signature.key_hash):
        raise exceptions.AccessDeniedException("Invalid key.")
    if signature_data.new_description:
        signature.description = signature_data.new_description
    if signature_data.new_value:
        signature.value = signature_data.new_value
    if signature_data.new_key:
        signature.key_hash = auth.hash_key(signature_data.new_key)
    await signature.save()
    logger.info(f"Updated signature {signature}")
    return models.response.ResponseSignature.from_db_model(signature)
