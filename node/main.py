from beanie import init_beanie
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from motor import motor_asyncio

from node import NODE_VERSION
from node.config import config
from node.exceptions import APIException, InternalServerErrorException
from node.models.database import Pool, Signature
from node.models.response import ResponseError
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
    title=f"evade84-node v{NODE_VERSION}",
    description="Fundamental system of anonymous communication.",
    version="0.1.0",
    docs_url="/swagger",
    redoc_url=None,
    # swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    openapi_tags=tags_metadata,
)


@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        logger.exception(exc)
        return JSONResponse(
            content=ResponseError(
                error_id="InternalServerError",
                error_message="Internal server error.",
                error_details=None,
            ).dict(),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(_, exc: RequestValidationError):
    return JSONResponse(
        content=ResponseError(
            error_id="UnprocessableEntity",
            error_message="Request validation error.",
            error_details=exc.errors(),
        ).dict(),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


@app.exception_handler(APIException)
async def api_exception_handler(_, exc: APIException):
    return JSONResponse(
        content=ResponseError(
            error_id=exc.__class__.__name__.replace("Exception", ""),
            error_message=exc.error_message,
            detail=None,
        ).dict(),
        status_code=exc.status_code,
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
