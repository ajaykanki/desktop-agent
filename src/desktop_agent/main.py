import uvicorn
from desktop_agent.api.app import create_app
from desktop_agent.settings.config import config

app = create_app()


def main():
    uvicorn.run(
        "desktop_agent.main:app",
        host=config.api.host,
        port=config.api.port,
        reload=config.is_dev,
        log_level="debug" if not config.is_dev else "info",
    )


if __name__ == "__main__":
    main()
