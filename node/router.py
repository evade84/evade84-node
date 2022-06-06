from fastapi import APIRouter
from loguru import logger
from pydantic import ValidationError

from node import auth, crud, exceptions, models, util

router = APIRouter()


@router.post(
    "/pool/new",
    name="Create a new pool",
    description="""Creates a new pool.""",
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
        logger.info(f"Generated new pool: {pool.uuid.hex}.")
        return pool
    except ValidationError as err:
        raise exceptions.IncorrectInputException(message=str(err))


@router.get(
    "/pool/{identifier}",
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
                message="Access denied for this pool."
            )


@router.get(
    "/pool/{identifier}/read",
    name="Read messages from pool",
    description="Returns list of messages from requested pool.",
    responses=util.generate_responses(
        "", [exceptions.PoolDoesNotExistException, exceptions.AccessDeniedException]
    ),
    response_model=list[models.db.Message],
)
async def read_pool(
    identifier: str,
    messages_count: int,
    master_key: str | None = None,
    reader_key: str | None = None,
):
    pool = await crud.get_pool(identifier)
    if not pool:
        raise exceptions.PoolDoesNotExistException()
    if pool.reader_key_hash:
        if reader_key:
            if not auth.verify_key(reader_key, pool.reader_key_hash):
                raise exceptions.AccessDeniedException(message="Invalid reader key.")
            return
        elif master_key:
            if not auth.verify_key(master_key, pool.master_key_hash):
                raise exceptions.AccessDeniedException(message="Invalid master key.")
            return await crud.read_messages(pool, messages_count)
        else:
            raise exceptions.ConflictException(
                message="Reader or master key required to access this pool."
            )
    else:
        return await crud.read_messages(pool, messages_count)


@router.put(
    "/pool/{identifier}/write",
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


@router.get(
    "/node",
    name="Get information about the node",
    description="",
    response_model=models.response.Node,
)
async def get_node_information():
    version = "0.1.0"
    pools_count = await models.db.Pool.count()
    return models.response.Node(version=version, pools_count=pools_count)
