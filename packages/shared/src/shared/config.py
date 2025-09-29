import os
import sys
import keyring
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from loguru import logger

env = os.getenv("ENV", "dev")
env_file = f".env.{env}" if env != "production" else ".env"
env_path = Path(env_file)

KEYRING_SERVICE = "desktop-agent"

if not env_path.exists():
    logger.error(f"Environment file {env_file} does not exist. Please create it.")
    raise FileNotFoundError(f"Environment file {env_file} does not exist.")


class APIConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file,
        env_prefix="API_",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    host: str = "0.0.0.0"
    port: int = 8000
    key: str | None = None
    key_header: str = "X-API-Key"
    prefix: str = "/api/v1"

    # Cors
    allowed_hosts: list = ["*"]
    cors_origins: list = ["*"]
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]

    title: str = "Task Queue API"
    version: str = "0.1.0"
    description: str = "A distributed task execution system with FastAPI server for task queue and workers for task execution"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.key:
            logger.warning(
                "API key is not set in environment variables. Retrieving from system keyring."
            )
            self.key = keyring.get_password(KEYRING_SERVICE, "api_key")


class DBConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file,
        env_prefix="DB_",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str | None = None
    name: str = "postgres"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.password:
            logger.warning(
                "Database password is not set in environment variables. Retrieving from system keyring."
            )
            self.password = keyring.get_password(KEYRING_SERVICE, "db_password")

    @property
    def url(self) -> str:
        return f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"




class LoggingConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file,
        env_prefix="LOG_",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    level: str = "INFO"
    format: str = (
        "<g>{time: DD-MM-YYYY hh:mm:ss A}</g> | <c>{extra[service]}</c> | <level> [{level}] | <m>{name}:{function}:{line}</m> {message}</level>"
        if env != "production"
        else "<g>{time: DD-MM-YYYY hh:mm:ss A}</g> | <m>{extra[service]}</m> | <level> [{level}] {message}</level>"
    )
    rotation: str = "100 MB"
    compression: str | None = None
    colorize: bool = True
    file: str | None = None
    error_file: str | None = None


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    env: str = env
    api: APIConfig = APIConfig()
    log: LoggingConfig = LoggingConfig()
    db: DBConfig = DBConfig()
    keyring_service: str | None = "desktop_agent"
    error: bool = False
    @property
    def is_dev(self) -> bool:
        return self.env.lower() == "dev"

    @property
    def is_production(self) -> bool:
        return self.env.lower() == "production"

    def validate_config(self):
        self.error = False
        if not self.api.key:
            logger.error("API key is not set in environment variables or keyring.")
            self.error = True

        if not self.db.password:
            logger.error(
                "Database password is not set in environment variables or keyring."
            )
            self.error = True

        if self.error:
            logger.error("Configuration validation failed. Please check the logs.")
            sys.exit(1)


config = ConfigBase()
config.validate_config()
