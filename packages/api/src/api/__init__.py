import uvicorn
from shared import config
from api.app import create_app

app = create_app()


def main():
    uvicorn.run(
        "api:app",
        host=config.api.host,
        port=config.api.port,
        reload=config.is_dev,
        log_level="warning" if not config.is_dev else "info",
    )
