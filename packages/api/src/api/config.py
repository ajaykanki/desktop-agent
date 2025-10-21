import os
from pydantic_settings import BaseSettings, SettingsConfigDict

PRODUCTION = ["prod", "production"]


def get_environment_file() -> str:
    """Determine the appropriate environment file based on the ENV variable."""
    env = os.getenv("ENV", "dev").lower()
    env_file = ".env" if env in PRODUCTION else f".env.{env}"
    return env_file


class APIConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_environment_file(),
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
        env_file=get_environment_file(),
        env_prefix="DB_",
        case_sensitive=False,
        extra="ignore",
    )

    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str | None = None
    name: str | None = "postgres"

    @property
    def url(self) -> str:
        return f"postgres://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class LoggingConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_environment_file(),
        env_prefix="LOG_",
        case_sensitive=False,
        extra="ignore",
    )

    level: str = "INFO"
    format: str = (
        "<g>{time: DD-MM-YYYY hh:mm:ss A}</g> | <m>{extra[service]}</m> | <level> [{level}] {message}</level>"
        if os.getenv("ENV", "dev") in PRODUCTION
        else "<g>{time: DD-MM-YYYY hh:mm:ss A}</g> | <c>{extra[service]}</c> | <level> [{level}] | <m>{name}:{function}:{line}</m> {message}</level>"
    )
    level: str = "INFO"
    rotation: str = "100 MB"
    retention: str = "7 days"
    compression: str = "zip"
    colorize: bool = True
    file: str | None = None
    error_file: str | None = None


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_environment_file(),
        case_sensitive=False,
        extra="ignore",
    )

    env: str = os.getenv("ENV", "dev")
    api: APIConfig = APIConfig()
    log: LoggingConfig = LoggingConfig()

    @property
    def is_dev(self) -> bool:
        return self.env.lower() == "dev"

    @property
    def is_production(self) -> bool:
        return self.env.lower() in PRODUCTION


config = Config()
