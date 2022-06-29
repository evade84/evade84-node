from fastapi import APIRouter

from node import NODE_VERSION, crud, models, util
from node.config import config

router = APIRouter(prefix="/node")


@router.get(
    "",
    summary="Get information about the current node",
    description="Returns current node information",
    responses=util.generate_responses("Returns current node information", []),
    response_model=models.response.ResponseNode,
)
async def get_node():
    pools_count = len(await crud.get_all_pools())
    return models.response.ResponseNode(
        name=config.NODE_NAME, version=NODE_VERSION, pools_count=pools_count
    )
