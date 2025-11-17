from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from scalar_fastapi import get_scalar_api_reference
from app.logging import log
from app.config import config
from .router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting FastAPI server...")
    try:
        # Initialize resources here
        if config.is_dev:
            log.success(f"Server started at http://localhost:{config.api.port}")
            log.info(f"Documentation at http://localhost:{config.api.port}/docs")

    except Exception as e:
        log.error(f"Error during server startup: {e}")
        raise e

    yield
    log.info("Stopping FastAPI server...")
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
    app.include_router(api_router, prefix=config.api.prefix)

    # Docs
    @app.get("/docs", include_in_schema=False)
    async def scalar_docs():
        return get_scalar_api_reference(
            openapi_url=app.openapi_url,
            title=app.title,
            dark_mode=True,
        )

    # Root
    @app.get("/", tags=["Root"])
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

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        log.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": exc.detail,
                "status_code": exc.status_code,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        log.error(f"Unhandled Exception: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=500,
            content={
                "message": "Internal server error",
                "status_code": 500,
            },
        )

    return app
