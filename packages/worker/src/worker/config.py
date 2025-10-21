import os
import keyring
import sys
from loguru import logger
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

KEYRING_SERVICE_NAME = os.getenv("KEYRING_SERVICE_NAME", "desktop-agent")
PRODUCTION = ["prod", "production"]


def get_environment_file() -> str:
    """Determine the appropriate environment file based on the ENV variable."""
    env = os.getenv("ENV", "dev").lower()
    env_file = ".env" if env in PRODUCTION else f".env.{env}"
    return env_file


def get_keyring_password(service_name: str, key_name: str) -> str:
    """Safely retrieve password from system keyring."""
    try:
        return keyring.get_password(service_name, key_name)
    except Exception as e:
        logger.warning(f"Failed to retrieve {key_name} from keyring: {e}")
        return None


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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.password:
            logger.warning(
                "DB_PASSWORD is not set in environment variables. Attempting to retrieve from system keyring."
            )
            self.password = get_keyring_password(KEYRING_SERVICE_NAME, "db_password")

    @property
    def url(self) -> str:
        return f"postgres://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class SAPConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_environment_file(),
        env_prefix="SAP_",
        case_sensitive=False,
        extra="ignore",
    )
    username: str | None = None
    password: str | None = None
    connection_name: str | None = "SAP 340 Quality"
    window_title: str = "SAP Logon 770"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.username:
            logger.warning(
                "SAP_USERNAME is not set in environment variables. Attempting to retrieve from system keyring."
            )
            self.username = get_keyring_password(KEYRING_SERVICE_NAME, "sap_username")

        if not self.password:
            logger.warning(
                "SAP_PASSWORD is not set in environment variables. Attempting to retrieve from system keyring."
            )
            self.password = get_keyring_password(KEYRING_SERVICE_NAME, "sap_password")


class APIConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_environment_file(),
        env_prefix="API_",
        case_sensitive=False,
        extra="ignore",
    )
    key: str | None = None
    key_header: str = "X-API-Key"
    base_url: str | None = "http://localhost:8000/api/v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.key:
            logger.warning(
                "API_KEY is not set in environment variables. Attempting to retrieve from system keyring."
            )
            self.key = get_keyring_password(KEYRING_SERVICE_NAME, "api_key")


class LoggingConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_environment_file(),
        env_prefix="LOG_",
        case_sensitive=False,
        extra="ignore",
    )
    level: str = "INFO"
    format: str = (
        "<g>{time: DD-MM-YYYY hh:mm:ss A}</g> | <level>[{level}] {message}</level>"
        if os.getenv("ENV", "dev") in PRODUCTION
        else "<g>{time: DD-MM-YYYY hh:mm:ss A}</g> | <level>[{level}]</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    rotation: str = "100 MB"
    retention: str = "7 days"
    compression: str = "zip"
    colorize: bool = True
    file: str | None = None
    error_file: str | None = None


class WorkerConfig(BaseModel):
    model_config = SettingsConfigDict(
        env_file=get_environment_file(),
        env_prefix="WORKER_",
        case_sensitive=False,
        extra="ignore",
    )
    concurrency: int = 1
    name: str | None = None
    queues: list[str] | str = "sap"
    import_paths: list[str] = ["worker.tasks"]


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_environment_file(),
        case_sensitive=False,
        extra="ignore",
    )
    env: str = os.getenv("ENV", "dev")
    api: APIConfig = APIConfig()
    db: DBConfig = DBConfig()
    sap: SAPConfig = SAPConfig()
    logging: LoggingConfig = LoggingConfig()
    worker: WorkerConfig = WorkerConfig()
    keyring_service_name: str = KEYRING_SERVICE_NAME

    @property
    def is_dev(self) -> bool:
        return self.env.lower() == "dev"

    @property
    def is_production(self) -> bool:
        return self.env.lower() in PRODUCTION

    def validate_config(self) -> bool:
        errors = []
        if not self.db.password:
            errors.append("DB_PASSWORD is not set in environment variables or keyring.")

        if not self.api.key:
            errors.append("API_KEY is not set in environment variables or keyring.")

        if not self.sap.username:
            errors.append(
                "SAP_USERNAME is not set in environment variables or keyring."
            )

        if not self.sap.password:
            errors.append(
                "SAP_PASSWORD is not set in environment variables or keyring."
            )

        if errors:
            for err in errors:
                logger.error(err)

            logger.error("Configuration validation failed.")
            return False

        return True


def _load_config():
    config = Config()
    if not config.validate_config():
        logger.error("Application cannot start.")
        sys.exit(1)

    return config


config = _load_config()
