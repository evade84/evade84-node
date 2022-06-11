from fastapi import APIRouter

from node import models, util
from node.config import config

router = APIRouter(prefix="/node")


@router.get(
    "",
    name="Get information about the current node",
    description="Returns current node information.",
    responses=util.generate_responses("Returns current node information.", []),
    response_model=models.response.ResponseNode,
)
async def get_node_information():
    version = "0.1.0"
    return models.response.ResponseNode(
        name=config.NODE_NAME,
        version=version,
    )
