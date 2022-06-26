from fastapi import APIRouter
from node import NODE_VERSION, models, util
from node.config import config

router = APIRouter(prefix="/node")


@router.get(
    "",
    name="Get information about the current node",
    description="Returns current node information.",
    responses=util.generate_responses("Returns current node information.", []),
    response_model=models.response.Node,
)
async def get_node():
    return models.response.Node(
        name=config.NODE_NAME,
        version=NODE_VERSION,
    )
