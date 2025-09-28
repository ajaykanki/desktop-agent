import uvicorn
from shared import config
from api.app import create_app

app = create_app()


def main():
    uvicorn.run(
        "api.main:app",
        host=config.api.host,
        port=config.api.port,
        reload=config.is_development,
        log_level="warning" if not config.is_development else "info",
    )


if __name__ == "__main__":
    main()
