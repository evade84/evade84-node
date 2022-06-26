from fastapi import APIRouter
from loguru import logger
from node import crud, exceptions, models

router = APIRouter(prefix="/signature")


@router.post(
    "/create",
    response_model=models.response.Signature,
    summary="Create signature",
    description="Creates new signature",
    response_description="Returns newly created signature",
)
async def create_signature(signature: models.request.NewSignature):
    db_signature = models.db.Signature.from_request(signature)
    await db_signature.create()
    logger.info(f"Created new signature: {db_signature}.")
    return models.response.Signature.from_db(db_signature)


@router.get("/{uuid}")
async def get_signature(uuid: str):
    signature = await crud.get_signature(uuid)
    if not signature:
        raise exceptions.SignatureNotFoundException()
    return models.response.Signature.from_db(signature)
