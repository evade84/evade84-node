from fastapi import APIRouter
from loguru import logger
from node import auth, crud, exceptions, models, slicing, util
from node.enums import PoolType

router = APIRouter(prefix="/pool")


@router.post(
    "/create",
    response_model=models.response.Pool,
    summary="Create pool",
    description="Creates new pool",
    responses=util.generate_responses(
        "returns newly created pool object",
        [exceptions.ConflictException, exceptions.IncorrectInputException],
    ),
)
async def create_pool(pool_type: PoolType, pool: models.request.NewPool):
    if not pool.validate_fields(pool_type):
        raise exceptions.IncorrectInputException("Invalid fields for this type of pool.")
    if pool.tag and await crud.get_pool(pool.tag):
        raise exceptions.ConflictException("Tag is already in use.")
    creator_signature = (
        await util.get_verified_signature(pool.creator_signature) if pool.creator_signature else None
    )
    db_pool = await models.db.Pool.from_request(
        pool_type=pool_type, pool=pool, creator_signature=creator_signature
    )
    await db_pool.create()
    logger.info(f"Created new pool: {db_pool}.")
    return models.response.Pool.from_db(db_pool)


@router.get(
    "/{identifier}",
    response_model=models.response.Pool,
    summary="Get pool",
    description="Returns requested pool object",
    responses=util.generate_responses(
        "Returns requested pool object",
        [exceptions.PoolDoesNotExistException, exceptions.AccessDeniedException],
    ),
)
async def get_pool(
    identifier: str, master_key: str | None, writer_key: str | None, reader_key: str | None
):
    pool = await crud.get_pool(identifier)
    if not pool:
        raise exceptions.PoolDoesNotExistException()
    if pool.public:
        return models.response.Pool.from_db(pool)
    else:
        if master_key:
            if not auth.verify_key(master_key, pool.master_key_hash):
                raise exceptions.AccessDeniedException(message="Invalid master key.")
            return models.response.Pool.from_db(pool)
        elif writer_key and pool.writer_key_hash:
            if not auth.verify_key(writer_key, pool.writer_key_hash):
                raise exceptions.AccessDeniedException(message="Invalid writer key.")
            return models.response.Pool.from_db(pool)
        elif reader_key and pool.reader_key_hash:
            if not auth.verify_key(reader_key, pool.reader_key_hash):
                raise exceptions.AccessDeniedException(message="Invalid reader key.")
        else:
            raise exceptions.AccessDeniedException(
                message="Access denied (master, writer or reader key is required)."
            )


@router.get(
    "/{identifier}/read",
    response_model=models.response.Messages,
    name="Read messages from pool",
    description="Returns list of messages from the requested pool",
    responses=util.generate_responses(
        "Returns list of messages from the requested pool",
        [
            exceptions.PoolDoesNotExistException,
            exceptions.AccessDeniedException,
            exceptions.IncorrectInputException,
        ],
    ),
)
async def read_pool(
    identifier: str,
    first: int | None = None,
    last: int | None = None,
    reader_key: str | None = None,
):
    slicing.validate_params(first, last)
    pool = await crud.get_pool(identifier)
    if not pool:
        raise exceptions.PoolDoesNotExistException()
    if pool.reader_key_hash:
        if reader_key:
            if not auth.verify_key(reader_key, pool.reader_key_hash):
                raise exceptions.AccessDeniedException("Invalid reader key.")
        else:
            raise exceptions.AccessDeniedException("Reader key is required to read this pool.")

    messages = slicing.slice_list(pool.messages, first, last)
    return models.response.Messages(
        AES_encrypted=pool.AES_encrypted,
        total=len(pool.messages),
        count=len(messages),
        messages=messages,
    )


@router.post(
    "/{identifier}/write",
    response_model=models.response.Message,
    name="Write a message to pool",
    description="Adds a new message to pool messages list, returns newly created message object",
    responses=util.generate_responses(
        "Returns newly created message object.",
        [exceptions.PoolDoesNotExistException, exceptions.AccessDeniedException],
    ),
)
async def write_to_pool(
    identifier: str,
    message: models.request.NewMessage,
    writer_key: str | None = None,
):
    pool = await crud.get_pool(identifier)
    if not pool:
        raise exceptions.PoolDoesNotExistException()
    if pool.writer_key_hash:
        if not writer_key:
            raise exceptions.AccessDeniedException("Writer key is required to write to this pool.")
        if not auth.verify_key(writer_key, pool.writer_key_hash):
            raise exceptions.AccessDeniedException("Invalid writer key.")

    signature = None
    print(message)
    if message.signature:
        signature = await crud.get_signature(message.signature.uuid)
        if not signature:
            raise exceptions.SignatureNotFoundException()
        if not auth.verify_key(message.signature.key, signature.key_hash):
            raise exceptions.AccessDeniedException("Invalid signature key.")

    db_message = await crud.write_message_to_pool(pool, message, signature)
    return db_message
