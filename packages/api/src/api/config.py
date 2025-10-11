import os
import sys
import keyring
from pydantic_settings import BaseSettings, SettingsConfigDict
from loguru import logger

# Define the keyring service name consistently
KEYRING_SERVICE_NAME = "desktop-agent"
PRODUDCTION = ["prod", "production"]


def get_environment_file() -> str:
    """Determine the appropriate environment file based on the ENV variable."""
    env = os.getenv("ENV", "dev").lower()
    env_file = ".env" if env in PRODUDCTION else f".env.{env}"
    return env_file


def get_keyring_password(service_name: str, key_name: str) -> str:
    """Safely retrieve password from system keyring."""
    try:
        return keyring.get_password(service_name, key_name)
    except Exception as e:
        logger.warning(f"Failed to retrieve {key_name} from keyring: {e}")
        return None


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
    name: str = "postgres"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.password:
            logger.warning(
                "Database password is not set in environment variables. Attempting to retrieve from system keyring."
            )
            self.password = get_keyring_password(KEYRING_SERVICE_NAME, "db_password")

    @property
    def url(self) -> str:
        return f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


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
        if os.getenv("ENV", "dev") in PRODUDCTION
        else "<g>{time: DD-MM-YYYY hh:mm:ss A}</g> | <c>{extra[service]}</c> | <level> [{level}] | <m>{name}:{function}:{line}</m> {message}</level>"
    )
    rotation: str = "100 MB"
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
    db: DBConfig = DBConfig()
    keyring_service_name: str = KEYRING_SERVICE_NAME

    @property
    def is_dev(self) -> bool:
        return self.env.lower() == "dev"

    @property
    def is_production(self) -> bool:
        return self.env.lower() in PRODUDCTION

    def validate_config(self) -> bool:
        errors = []
        if not self.db.password:
            errors.append(
                "Database password is not set in environment variables or keyring."
            )

        if errors:
            for error in errors:
                logger.error(error)
            logger.error("Configuration validation failed.")
            return False
        return True


def _load_config():
    config = Config()
    if not config.validate_config():
        logger.error("Configuration validation failed. Application cannot start.")
        sys.exit(1)

    return config


config = _load_config()
