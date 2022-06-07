from fastapi import APIRouter

from node import models, util

router = APIRouter(prefix="/node")


@router.get(
    "/",
    name="Get information about the current node",
    description="Returns current node information.",
    responses=util.generate_responses("Returns current node information.", []),
    response_model=models.response.Node,
)
async def get_node_information():
    version = "0.1.0"
    indexable_pools_count = await models.db.Pool.find(
        models.db.Pool.indexable == True
    ).count()
    return models.response.Node(
        version=version, indexable_pools_count=indexable_pools_count
    )
