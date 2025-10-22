import os
import sys
from api.logger import logger
from pydantic_settings import BaseSettings, SettingsConfigDict

PRODUCTION = ["prod", "production"]
ENV = os.getenv("ENV", "dev").lower()


def get_env_file() -> str:
    """Get the appropriate environment file based on the current environment."""
    env_file = ".env" if ENV in PRODUCTION else f".env.{ENV}"
    return env_file


class APIConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        env_prefix="API_",
        case_sensitive=False,
        extra="ignore",
    )

    host: str = "0.0.0.0"
    port: int = 8000
    key_header: str = "X-API-Key"
    prefix: str = "/api/v1"

    # Meta
    title: str = "Task Queue API"
    version: str = "0.1.0"
    description: str = "A distributed task execution system with FastAPI server for task queue and workers for task execution"


class DBConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        env_prefix="DB_",
        case_sensitive=False,
        extra="ignore",
    )

    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str | None = None
    name: str | None = "postgres"

    def model_post_init(self, __context) -> None:
        """Post initialization hook to handle keyring password retrieval."""
        if not self.password:
            logger.warning(
                "DB_PASSWORD is not set in environment variables. Attempting to retrieve from system keyring."
            )

    @property
    def url(self) -> str:
        return f"postgres://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        case_sensitive=False,
        extra="ignore",
    )

    env: str = ENV
    api: APIConfig = APIConfig()
    db: DBConfig = DBConfig()

    @property
    def is_dev(self) -> bool:
        return self.env == "dev"

    @property
    def is_production(self) -> bool:
        return self.env in PRODUCTION

    def validate_config(self) -> bool:
        """
        Validate the configuration settings.

        Returns:
            True if all required configurations are set, False otherwise
        """
        errors = []
        if not self.db.password:
            errors.append("DB_PASSWORD is not set in environment variables or keyring.")

        if errors:
            for err in errors:
                logger.error(err)

            logger.error("Configuration validation failed.")
            return False

        return True


def _load_config() -> Config:
    """
    Load and validate the application configuration.

    Returns:
        A validated Config instance

    Raises:
        SystemExit: If configuration validation fails
    """
    config = Config()
    if not config.validate_config():
        logger.error("Application cannot start.")
        sys.exit(1)

    return config


config = _load_config()
