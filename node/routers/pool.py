from fastapi import APIRouter
from loguru import logger
from pydantic import ValidationError

from node import auth, crud, exceptions, models, slicing, util

router = APIRouter(prefix="/pool")


@router.post(
    "/new",
    name="Create a new pool",
    description="Creates a new pool.",
    response_model=models.response.Pool,
    responses=util.generate_responses(
        "Returns a newly crated pool object.",
        exceptions=[
            exceptions.ConflictException,
            exceptions.IncorrectInputException,
        ],
    ),
)
async def new_pool(body: models.request.Pool):
    if body.tag:
        if await crud.get_pool(body.tag):
            raise exceptions.ConflictException(message="Tag is already in use.")

    master_key_hash = None
    reader_key_hash = None

    if body.reader_key:
        if not body.master_key:
            raise exceptions.IncorrectInputException(
                message="Master key must be specified if reader key was indicated."
            )
        reader_key_hash = auth.hash_key(body.reader_key)
    if body.master_key:
        master_key_hash = auth.hash_key(body.master_key)
    try:
        pool = models.db.Pool(
            tag=body.tag,
            creator=body.creator,
            description=body.description,
            indexable=body.indexable,
            master_key_hash=master_key_hash,
            reader_key_hash=reader_key_hash,
        )
        await pool.create()
        logger.info(f"Created new pool: {pool.uuid.hex}.")
        return pool
    except ValidationError as err:
        raise exceptions.IncorrectInputException(message=str(err))


@router.get(
    "/list",
    name="Get list of all indexable pools",
    description="Returns list of all indexable pools.",
    responses=util.generate_responses(
        "Returns list of all indexable pools.",
        [],
    ),
    response_model=models.response.Pools,
)
async def get_all_indexable_pools(first: int | None = None, last: int | None = None):
    slicing.validate_params(first, last)
    pools = await models.db.Pool.find(
        models.db.Pool.indexable == True  # noqa
    ).to_list()
    sliced_pools = slicing.slice_list(pools, first, last)
    return models.response.Pools(total=len(pools), pools=sliced_pools)


@router.get(
    "/{identifier}",
    name="Get information about pool",
    description="Returns requested pool object.",
    responses=util.generate_responses(
        "Returns requested pool object.",
        [exceptions.PoolDoesNotExistException, exceptions.AccessDeniedException],
    ),
    response_model=models.response.Pool,
)
async def get_pool_info(
    identifier: str, master_key: str | None = None, reader_key: str | None = None
):
    pool = await crud.get_pool(identifier)
    if not pool:
        raise exceptions.PoolDoesNotExistException()
    if pool.indexable:
        return pool
    else:
        if master_key:
            if auth.verify_key(master_key, pool.reader_key_hash):
                return pool
        elif reader_key:
            if auth.verify_key(reader_key, pool.reader_key_hash):
                return pool
        else:
            raise exceptions.AccessDeniedException(
                message="Access denied to this pool."
            )


@router.get(
    "/{identifier}/read",
    name="Read messages from pool",
    description="Returns list of messages from the requested pool.",
    responses=util.generate_responses(
        "Returns list of messages from the requested pool.",
        [
            exceptions.PoolDoesNotExistException,
            exceptions.AccessDeniedException,
            exceptions.IncorrectInputException,
        ],
    ),
    response_model=models.response.Messages,
)
async def read_pool(
    identifier: str,
    first: int | None = None,
    last: int | None = None,
    master_key: str | None = None,
    reader_key: str | None = None,
):
    slicing.validate_params(first, last)
    pool = await crud.get_pool(identifier)
    if not pool:
        raise exceptions.PoolDoesNotExistException()
    if pool.reader_key_hash:
        if reader_key:
            if not auth.verify_key(reader_key, pool.reader_key_hash):
                raise exceptions.AccessDeniedException(message="Invalid reader key.")
        elif master_key:
            if not auth.verify_key(master_key, pool.master_key_hash):
                raise exceptions.AccessDeniedException(message="Invalid master key.")
        else:
            raise exceptions.ConflictException(
                message="Reader key or master key is required to access this pool."
            )
    messages = slicing.slice_list(pool.messages, first, last)
    return models.response.Messages(total=len(pool.messages), messages=messages)


@router.put(
    "/{identifier}/write",
    name="Write a message to pool",
    description="Adds a new message to pool messages list, returns newly created message object.",
    responses=util.generate_responses(
        "Returns newly created message object.",
        [exceptions.PoolDoesNotExistException, exceptions.AccessDeniedException],
    ),
    response_model=models.db.Message,
)
async def write_to_pool(
    identifier: str,
    text: str,
    signature: str | None = None,
    master_key: str | None = None,
):
    pool = await crud.get_pool(identifier)
    if not pool:
        raise exceptions.PoolDoesNotExistException()
    if pool.master_key_hash:
        if not master_key:
            raise exceptions.ConflictException(
                message="Master key is required to write to this pool."
            )
        if not auth.verify_key(master_key, pool.master_key_hash):
            raise exceptions.AccessDeniedException(message="Invalid master key.")
        return await crud.write_message(pool, text, signature)
    else:
        return await crud.write_message(pool, text, signature)
