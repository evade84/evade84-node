from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from node import NODE_VERSION, util
from node.config import config

router = APIRouter(prefix="")
templates = Jinja2Templates(directory="node/templates")


@router.get(
    "/",
    summary="Welcome page",
    description="Returns welcoming HTML page.",
    responses=util.generate_responses("Returns a HTML page", api_exceptions=[]),
)
async def root(request: Request):
    return templates.TemplateResponse(
        "root.html",
        {
            "request": request,
            "node_name": config.NODE_NAME,
            "node_description": config.NODE_DESCRIPTION,
            "node_version": NODE_VERSION,
        },
    )
