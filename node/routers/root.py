from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from node.config import config

router = APIRouter(prefix="")


@router.get("/", name="Root", description="Nothing interesting here.")
async def redirect_to_node_info():
    return HTMLResponse(
        content=f"evade84-node 0.1.0 ({config.NODE_NAME}) is running."
        "<ul>"
        "<li><a href='/docs'>node API docs</li>"
        "<li><a href='https://example.com'>manual</li>"
        "<li><a href='https://github.com/evade84'>project at github</li>"
        "</ul>"
    )
