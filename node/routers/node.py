import time

from fastapi import APIRouter

from node import NODE_VERSION, START_TIME, models, util
from node.config import config

router = APIRouter(prefix="/node")


@router.get(
    "",
    summary="Get information about the current node",
    description="Returns current node information.",
    responses=util.generate_responses("Returns current node information.", api_exceptions=[]),
    response_model=models.response.ResponseNode,
)
async def get_node():
    pools_count = await models.database.Pool.count()
    signatures_count = await models.database.Signature.count()

    return models.response.ResponseNode(
        name=config.NODE_NAME,
        description=config.NODE_DESCRIPTION,
        version=NODE_VERSION,
        uptime_sec=time.time() - START_TIME,
        pools_count=pools_count,
        signatures_count=signatures_count,
    )
