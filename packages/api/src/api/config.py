import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from loguru import logger

env = os.getenv("ENV", "dev")
env_file = f".env.{env}" if env != "production" else ".env"
env_path = Path(env_file)

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

    title: str = "Task Execution API"
    version: str = "0.1.0"
    description: str = (
        "A distributed task execution system with FastAPI API server and workers"
    )


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


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    env: str = env
    api: APIConfig = APIConfig()
    log: LoggingConfig = LoggingConfig()

    @property
    def is_dev(self) -> bool:
        return self.env.lower() == "dev"

    @property
    def is_production(self) -> bool:
        return self.env.lower() == "production"


config = Config()
