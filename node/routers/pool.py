from datetime import datetime

import beanie
from fastapi import APIRouter
from loguru import logger
from node import auth, crud, exceptions, models, util, validators

router = APIRouter(prefix="/pool")


@router.post(
    "/new",
    name="Create a new pool",
    description="Creates a new pool.",
    responses=util.generate_responses(
        "Returns newly crated pool object.",
        exceptions=[
            exceptions.ConflictException,
            exceptions.IncorrectInputException,
            exceptions.SignatureDoesNotExistException,
            exceptions.AccessDeniedException,
        ],
    ),
    response_model=models.response.ResponsePool,
)
async def create_pool(pool: models.request.RequestPool):
    pool.validate_creator_signature_fields()
    if pool.writer_key and pool.reader_key and pool.public:
        raise exceptions.IncorrectInputException("Public pool can't have both `writer_key` and `reader_key`.")

    if pool.tag:
        if await crud.pool_exists(pool.tag):
            raise exceptions.ConflictException("Tag is already in use.")

    creator_signature: models.db.Signature | None = None
    if pool.creator_signature_tag:
        creator_signature = await crud.get_signature(pool.creator_signature_tag)
        if not creator_signature:
            raise exceptions.SignatureDoesNotExistException("Signature does not exist.")
        if not auth.verify_key(pool.creator_signature_key, creator_signature.key_hash):
            raise exceptions.AccessDeniedException("Invalid signature key.")

    master_key_hash = auth.hash_key(pool.master_key)
    writer_key_hash = auth.hash_key(pool.writer_key) if pool.writer_key else None
    reader_key_hash = auth.hash_key(pool.reader_key) if pool.reader_key else None

    creation_date = datetime.now() if not pool.hide_creation_date else None

    db_pool = models.db.Pool(
        tag=pool.tag,
        public=pool.public,
        description=pool.description,
        creator_signature=creator_signature,
        creation_date=creation_date,
        master_key_hash=master_key_hash,
        writer_key_hash=writer_key_hash,
        reader_key_hash=reader_key_hash,
    )
    await db_pool.create()
    logger.info(f"Created new pool {db_pool}.")
    return models.response.ResponsePool.from_db_pool(db_pool)


@router.get(
    "/list",
    name="Get list of all public pools",
    description="Returns list of all public pool objects.",
    responses=util.generate_responses(
        "Returns list of all public pool objects.",
        [exceptions.IncorrectInputException],
    ),
    response_model=models.response.ResponsePools,
)
async def get_indexable_pools_list(first: int | None = None, last: int | None = None):
    validators.validate_slicing(first, last)
    pools = await crud.get_public_pools()
    return models.response.ResponsePools.from_pools(total=len(pools), pools=util.slice_list(pools, first, last))


@router.get(
    "/{identifier}",
    name="Get pool information",
    description="Returns requested pool object.",
    responses=util.generate_responses(
        "Returns requested pool object.",
        [exceptions.PoolDoesNotExistException, exceptions.AccessDeniedException],
    ),
    response_model=models.response.ResponsePool,
)
async def get_pool_info(
    identifier: str,
    master_key: str | None = None,
    writer_key: str | None = None,
    reader_key: str | None = None,
):
    pool = await crud.get_pool(identifier)
    if not pool:
        raise exceptions.PoolDoesNotExistException()
    if not pool.public:
        if master_key:
            if not auth.verify_key(master_key, pool.master_key_hash):
                raise exceptions.AccessDeniedException("Invalid master key.")
        elif writer_key:
            if not auth.verify_key(writer_key, pool.writer_key_hash):
                raise exceptions.AccessDeniedException("Invalid writer key.")
        elif reader_key and pool.reader_key_hash:
            if not auth.verify_key(reader_key, pool.reader_key_hash):
                raise exceptions.AccessDeniedException("Invalid reader key.")
        else:
            raise exceptions.AccessDeniedException("Access denied (master, writer or reader key is required).")
    return models.response.ResponsePool.from_db_pool(pool)


@router.get(
    "/{identifier}/read",
    name="Read messages from pool",
    description="Returns list of messages from the requested pool.",
    responses=util.generate_responses(
        "Returns list of message objects from the requested pool.",
        [
            exceptions.PoolDoesNotExistException,
            exceptions.AccessDeniedException,
            exceptions.IncorrectInputException,
        ],
    ),
    response_model=models.response.ResponseMessages,
)
async def get_pool_messages(
    identifier: str,
    first: int | None = None,
    last: int | None = None,
    reader_key: str | None = None,
):
    validators.validate_slicing(first, last)
    pool = await crud.get_pool(identifier)
    if not pool:
        raise exceptions.PoolDoesNotExistException()
    if pool.reader_key_hash:
        if not reader_key:
            raise exceptions.AccessDeniedException("Reader key is required to access this pool.")
        if not auth.verify_key(reader_key, pool.reader_key_hash):
            raise exceptions.AccessDeniedException(message="Invalid reader key.")
    return models.response.ResponseMessages.from_messages(
        total=len(pool.messages), messages=util.slice_list(pool.messages, first, last)
    )


@router.post(
    "/{identifier}/write",
    name="Write a new message to pool",
    description="Writes a new message to pool, returns a newly created message object.",
    responses=util.generate_responses(
        "Returns newly created message object.",
        [
            exceptions.IncorrectInputException,
            exceptions.PoolDoesNotExistException,
            exceptions.AccessDeniedException,
        ],
    ),
    response_model=models.response.ResponseMessage,
)
async def write_message_to_pool(
    identifier: str,
    message: models.request.RequestMessage,
):
    message.validate_message_signature_fields()
    pool = await crud.get_pool(identifier)
    if not pool:
        raise exceptions.PoolDoesNotExistException()

    signature: models.db.Signature | None = None
    if message.signature_tag and message.signature_tag:
        signature = await crud.get_signature(message.signature_tag)
        if not signature:
            raise exceptions.SignatureDoesNotExistException("Signature does not exist.")
        if not auth.verify_key(message.signature_key, signature.key_hash):
            raise exceptions.AccessDeniedException("Invalid signature key.")
    if pool.writer_key_hash:
        if not message.writer_key:
            raise exceptions.AccessDeniedException("Writer key is required to write to this pool.")
        if not auth.verify_key(message.writer_key, pool.writer_key_hash):
            raise exceptions.AccessDeniedException("Invalid writer key.")

    id = len(pool.messages) + 1  # noqa
    db_message = models.db.Message(
        id=id,
        text=message.text,
        signature=signature,
        date=datetime.now() if not message.hide_message_date else None,
    )
    pool.messages.append(db_message)
    await pool.save(link_rule=beanie.WriteRules.WRITE)
    logger.info(f"New message in pool {pool}: {db_message}.")

    return models.response.ResponseMessage.from_db_message(db_message)


@router.delete(
    "/{identifier}/delete",
    name="Delete pool",
    description="Completely deletes specified pool.",
    responses=util.generate_responses(
        "Returns deleted pool object.",
        [exceptions.PoolDoesNotExistException, exceptions.AccessDeniedException],
    ),
    response_model=models.response.ResponsePool,
)
async def delete_pool(identifier: str, master_key: str):
    pool = await crud.get_pool(identifier)
    if not pool:
        raise exceptions.PoolDoesNotExistException()
    if not auth.verify_key(master_key, pool.master_key_hash):
        raise exceptions.AccessDeniedException("Invalid master key.")
    await pool.delete()
    logger.info(f"Deleted pool {pool}.")
    return models.response.ResponsePool.from_db_pool(pool)
