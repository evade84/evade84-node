from beanie import init_beanie
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from loguru import logger
from motor import motor_asyncio

from node.config import config
from node.exceptions import APIErrorException
from node.models.db import Pool
from node.models.response import ResponseError
from node.routers.node import router as node_router
from node.routers.pool import router as pool_router
from node.routers.root import router as root_router

app = FastAPI(
    title=f"evade84-node ({config.NODE_NAME})",
    description="Fundamental system of anonymous communication.",
    version="0.1.0",
    redoc_url=None,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)


@app.exception_handler(APIErrorException)
async def api_error_exception_handler(_, exc: APIErrorException):
    return JSONResponse(
        content=ResponseError(error_message=exc.error_message).dict(),
        status_code=exc.status_code,
    )


@app.on_event("startup")
async def on_startup():
    client = motor_asyncio.AsyncIOMotorClient(
        f"mongodb://{config.MONGO_HOST}:{config.MONGO_PORT}/{config.MONGO_DB}"
    )

    await init_beanie(client[config.MONGO_DB], document_models=[Pool])
    logger.info("Initialized database.")
    app.include_router(node_router)
    app.include_router(pool_router)
    app.include_router(root_router)
