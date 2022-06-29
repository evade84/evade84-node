from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from node import NODE_VERSION, util
from node.config import config

router = APIRouter(prefix="")


@router.get(
    "/",
    summary="root route",
    description="Returns welcoming HTML page",
    responses=util.generate_responses("Returns a HTML page", api_exceptions=[]),
)
async def root():
    css = """
    <style>
    * {font-family: monospace;}
    a {font-size: 20px;}
    b {font-size: 25px;}
    </style>
    """
    content = (
        css
        + f"""
    <b>Welcome to evade84-node v{NODE_VERSION} ({config.NODE_NAME})</b>.
    <ul>
    <li><a href="/swagger">swagger ui (API documentation)</a></li>
    <li><a href="https://evade84.github.io">docs and more info</a></li>
    <li><a href="https://github.com/evade84">project at github</a></li>
    </ul>
    """
    )
    return HTMLResponse(content=content)
