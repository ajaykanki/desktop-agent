from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from shared import config
from api.logger import log
from api.exceptions import HTTPException
from api.utils import get_local_ip


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting FastAPI server...")
    try:
        # Initialize resources here
        # db.initialize()
        log.success(
            f"Server running at http://{get_local_ip() if config.api.host == '0.0.0.0' else config.api.host}:"
            f"{config.api.port}"
        )
        pass
    except Exception as e:
        log.error(f"Error during server startup: {e}")
        raise e

    yield
    log.info("Stopping FastAPI server...")
    # Cleanup resources here
    # db.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title=config.api.title,
        description=config.api.description,
        version=config.api.version,
        lifespan=lifespan,
        docs_url="/swagger-docs",
    )

    # middlewares
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.api.cors_origins,
        allow_methods=config.api.cors_methods,
        allow_headers=config.api.cors_headers,
        allow_credentials=True,
    )

    # Register routers here
    # app.include_router(TaskRouter, prefix=config.api.prefix)

    # Docs
    @app.get("/docs", include_in_schema=False)
    async def scalar_docs():
        return get_scalar_api_reference(
            openapi_url=app.openapi_url,
            title=app.title,
            dark_mode=True,
        )

    # Exception handlers
    @app.exception_handler(HTTPException)
    async def custom_http_exception_handler(request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": exc.error, "message": exc.message},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        log.error(f"Unhandled exception: {str(exc)}")
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
