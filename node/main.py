from beanie import init_beanie
from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from motor import motor_asyncio

from node.config import config
from node.exceptions import APIErrorException
from node.models.db import Pool, Signature
from node.models.response import ResponseError, ResponseRequestValidationError
from node.routers.node import router as node_router
from node.routers.pool import router as pool_router
from node.routers.root import router as root_router
from node.routers.signature import router as signature_router

tags_metadata = [
    {
        "name": "node",
        "description": "node information",
        "externalDocs": {
            "description": "About nodes",
            "url": "https://evade84.github.io/getting-started/basic-definitions/#node",
        },
    },
    {
        "name": "pool",
        "description": "operations with pools",
        "externalDocs": {
            "description": "About pools",
            "url": "https://evade84.github.io/getting-started/basic-definitions/#pool",
        },
    },
    {
        "name": "signature",
        "description": "operations with signatures",
        "externalDocs": {
            "description": "About signatures",
            "url": "https://evade84.github.io/getting-started/basic-definitions/#signature",
        },
    },
    {"name": "root", "description": "root route"},
]

app = FastAPI(
    title=f"evade84-node ({config.NODE_NAME})",
    description="Fundamental system of anonymous communication.",
    version="0.1.0",
    docs_url="/swagger",
    redoc_url=None,
    # swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    openapi_tags=tags_metadata,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError):
    return JSONResponse(
        content=ResponseRequestValidationError(
            error_message="Request validation error.", detail=exc.errors()
        ).dict(),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


@app.exception_handler(APIErrorException)
async def api_error_exception_handler(_, exc: APIErrorException):
    return JSONResponse(
        content=ResponseError(error_message=exc.error_message).dict(), status_code=exc.status_code
    )


@app.on_event("startup")
async def on_startup():
    client = motor_asyncio.AsyncIOMotorClient(
        f"mongodb://{config.MONGO_HOST}:{config.MONGO_PORT}/{config.MONGO_DB}"
    )
    await init_beanie(client[config.MONGO_DB], document_models=[Pool, Signature])
    logger.info("Connected to the database.")
    app.include_router(root_router, tags=["root"])
    app.include_router(node_router, tags=["node"])
    app.include_router(signature_router, tags=["signature"])
    app.include_router(pool_router, tags=["pool"])
