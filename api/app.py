from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from scalar_fastapi import get_scalar_api_reference

from logger import logger
from settings.config import config
from api.utils import get_local_ip


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FastAPI server...")
    try:
        # Initialize resources here
        logger.success(
            f"Server running at http://{get_local_ip() if config.api.host == '0.0.0.0' else config.api.host}:"
            f"{config.api.port}"
        )
        pass
    except Exception as e:
        logger.error(f"Error during server startup: {e}")
        raise e

    yield
    logger.info("Stopping FastAPI server...")
    # Cleanup resources here


def create_app() -> FastAPI:
    app = FastAPI(
        title=config.api.title,
        description=config.api.description,
        version=config.api.version,
        lifespan=lifespan,
        docs_url="/swagger-docs",
    )

    # Register routers here

    # Docs
    @app.get("/docs", include_in_schema=False)
    async def scalar_docs():
        return get_scalar_api_reference(
            openapi_url=app.openapi_url,
            title=app.title,
            dark_mode=True,
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        logger.error(f"Unhandled exception: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal Server Error",
                "message": "An unexpected error occurred.",
            },
        )

    # Root
    @app.get("/")
    async def root():
        return {
            "name": config.api.title,
            "version": config.api.version,
            "description": config.api.description,
            "timestamp": datetime.strftime(
                datetime.now(timezone.utc), "%Y-%m-%d %H:%M:%S"
            ),
            "environment": config.env,
        }

    return app
