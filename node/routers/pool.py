from typing import Union

from fastapi import APIRouter
from loguru import logger

from node import auth, crud, exceptions, models, slicing, util
from node.enums import MessageType, PoolType

router = APIRouter(prefix="/pool")


@router.post(
    "/create",
    response_model=models.response.ResponsePool,
    summary="Create a new pool",
    description="Creates new pool",
    responses=util.generate_responses(
        "Returns newly created pool object",
        [exceptions.ConflictException, exceptions.IncorrectInputException],
    ),
)
async def create_pool(
    type: PoolType,  # noqa
    new_pool: models.request.RequestNewPool,
):
    errors = new_pool.validate_based_on_type(type)
    if errors:
        raise exceptions.IncorrectInputException(
            util.build_errors_message("Incorrect pool fields", errors)
        )

    if new_pool.tag and await crud.get_pool(new_pool.tag):
        raise exceptions.ConflictException("Tag is already in use.")
    creator_signature = (
        await util.get_verified_signature(new_pool.creator_signature)
        if new_pool.creator_signature
        else None
    )
    db_pool = models.database.Pool.from_request_model(type, new_pool, creator_signature)
    await db_pool.save()
    logger.info(f"Created new pool: {db_pool}.")
    return models.response.ResponsePool.from_db_model(db_pool)


@router.get(
    "/list",
    response_model=models.response.ResponsePools,
    summary="Get list of all public pools",
    description="Returns list of public pool objects",
    responses=util.generate_responses("Returns list of public pool objects", []),
)
async def list_public_pools(first: int | None = None, last: int | None = None):
    slicing.validate_params(first, last)
    pools = await crud.get_public_pools()
    target_pools = slicing.slice_list(pools, first, last)
    return models.response.ResponsePools(
        total=len(pools),
        count=len(target_pools),
        pools=[models.response.ResponsePool.from_db_model(db_pool) for db_pool in target_pools],
    )


@router.get(
    "/{identifier}",
    response_model=models.response.ResponsePool,
    summary="Get pool information",
    description="Returns requested pool object",
    responses=util.generate_responses(
        "Returns requested pool object",
        [exceptions.PoolDoesNotExistException, exceptions.AccessDeniedException],
    ),
)
async def get_pool(
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
                raise exceptions.InvalidMasterKeyException()
        elif writer_key and pool.writer_key_hash:
            if not auth.verify_key(writer_key, pool.writer_key_hash):
                raise exceptions.InvalidWriterKeyException()
        elif reader_key and pool.reader_key_hash:
            if not auth.verify_key(reader_key, pool.reader_key_hash):
                raise exceptions.InvalidReaderKeyException()
        else:
            raise exceptions.AccessDeniedException(
                "The pool is not public: master, writer or reader key is required to get information about this pool."
            )
    logger.info(f"Returned info about pool {pool}.")
    return models.response.ResponsePool.from_db_model(pool)


@router.get(
    "/{identifier}/read",
    response_model=models.response.ResponseMessages,
    summary="Read messages from pool",
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
                raise exceptions.InvalidReaderKeyException()
        else:
            raise exceptions.AccessDeniedException("Reader key is required to read this pool.")

    messages = slicing.slice_list(pool.messages, first, last)
    logger.info(f"Read some messages from pool {pool}.")
    return models.response.ResponseMessages(
        encrypted=pool.encrypted,
        total=len(pool.messages),
        count=len(messages),
        messages=messages,
    )


@router.post(
    "/{identifier}/write",
    response_model=Union[
        models.response.ResponsePlaintextMessage, models.response.ResponseEncryptedMessage
    ],
    summary="Write a message to pool",
    description="Adds a new message to pool messages list, returns newly created message object",
    responses=util.generate_responses(
        "Returns newly created message object.",
        [exceptions.PoolDoesNotExistException, exceptions.AccessDeniedException],
    ),
)
async def write_to_pool(
    identifier: str,
    message_type: MessageType,
    message: models.request.RequestNewMessage,
    writer_key: str | None = None,
):
    errors = message.validate_based_on_type(message_type)
    if errors:
        raise exceptions.IncorrectInputException(
            util.build_errors_message("Invalid message fields", errors)
        )

    pool = await crud.get_pool(identifier)
    if not pool:
        raise exceptions.PoolDoesNotExistException()

    if pool.writer_key_hash:
        if not writer_key:
            raise exceptions.AccessDeniedException("Writer key is required to write to this pool.")
        if not auth.verify_key(writer_key, pool.writer_key_hash):
            raise exceptions.AccessDeniedException("Invalid writer key.")

    if pool.encrypted != (message_type == MessageType.encrypted):
        raise exceptions.ConflictException(
            "Pool encryption settings does not match with the message type "
            "(you are sending plaintext message to an encrypted pool or vise versa)."
        )

    signature = await util.get_verified_signature(message.signature) if message.signature else None
    db_message = await crud.write_message_to_pool(pool, message_type, message, signature)
    logger.info(f"Wrote a new message to pool {pool}: {db_message}.")

    match db_message.type:
        case MessageType.plaintext:
            return models.response.ResponsePlaintextMessage.from_db_model(db_message)
        case MessageType.encrypted:
            return models.response.ResponseEncryptedMessage.from_db_model(db_message)
        case _:
            raise ValueError("Invalid message type.")


@router.post(
    "/{identifier}/update",
    response_model=models.response.ResponsePool,
    summary="Update pool",
    description="Updates some pool fields",
    responses=util.generate_responses("Returns updated pool object", [exceptions.AccessDeniedException]),
)
async def update_pool(identifier: str, master_key: str, pool_data: models.request.RequestUpdatePool):
    pool = await crud.get_pool(identifier)
    if not pool:
        raise exceptions.PoolDoesNotExistException()
    if not auth.verify_key(master_key, pool.master_key_hash):
        raise exceptions.InvalidMasterKeyException()

    if pool_data.new_description:
        pool.description = pool_data.new_description
    if pool_data.new_master_key:
        pool.master_key_hash = auth.hash_key(pool_data.new_master_key)
    if pool_data.new_writer_key:
        pool.writer_key_hash = auth.hash_key(pool_data.new_writer_key)
    if pool_data.new_reader_key:
        pool.reader_key_hash = auth.hash_key(pool_data.new_reader_key)
    await pool.save()
    logger.info(f"Updated pool {pool}.")
    return models.response.ResponsePool.from_db_model(pool)


@router.delete(
    "/{identifier}/delete",
    response_model=models.response.ResponsePool,
    summary="Delete pool",
    description="Deletes pool",
    responses=util.generate_responses(
        "Returns deleted pool object.",
        [exceptions.AccessDeniedException, exceptions.PoolDoesNotExistException],
    ),
)
async def delete_pool(identifier: str, master_key: str):
    pool = await crud.get_pool(identifier)
    if not pool:
        raise exceptions.PoolDoesNotExistException()
    if not auth.verify_key(master_key, pool.master_key_hash):
        raise exceptions.InvalidMasterKeyException()
    await pool.delete()
    logger.info(f"Deleted pool {pool}.")
    return models.response.ResponsePool.from_db_model(pool)
