from fastapi import APIRouter
from fastapi.responses import RedirectResponse


router = APIRouter(prefix="")


@router.get("/")
async def redirect_to_node_info():
    return RedirectResponse("/node")
