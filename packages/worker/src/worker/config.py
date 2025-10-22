import os
import keyring
import sys
from typing import Optional, List, Union
from worker.logger import logger
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

KEYRING_SERVICE_NAME = os.getenv("KEYRING_SERVICE_NAME", "desktop-agent")
PRODUCTION = ["prod", "production"]
ENV = os.getenv("ENV", "dev").lower()


def get_env_file() -> str:
    """Get the appropriate environment file based on the current environment."""
    env_file = ".env" if ENV in PRODUCTION else f".env.{ENV}"
    return env_file


def get_keyring_password(service_name: str, key_name: str) -> str | None:
    """
    Safely retrieve password from system keyring.

    Args:
        service_name: The name of the service to retrieve from keyring
        key_name: The key name to retrieve from keyring

    Returns:
        The password string if found, None otherwise
    """
    try:
        password = keyring.get_password(service_name, key_name)
        if password is None:
            logger.debug(f"No keyring entry found for {key_name}")

        return password
    except Exception as e:
        logger.warning(f"Failed to retrieve {key_name} from keyring: {e}")
        return None


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
    password: Optional[str] = None
    name: Optional[str] = "postgres"

    def model_post_init(self, __context) -> None:
        """Post initialization hook to handle keyring password retrieval."""
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
        env_file=get_env_file(),
        env_prefix="SAP_",
        case_sensitive=False,
        extra="ignore",
    )

    username: str | None = None
    password: str | None = None
    connection_name: str | None = "SAP 340 Quality"
    window_title: str = "SAP Logon 770"
    executable_path: str = r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe"

    def model_post_init(self, __context) -> None:
        """Post initialization hook to handle keyring username and password retrieval."""
        if not self.username:
            logger.warning(
                "SAP_USERNAME is not set in environment variables. Attempting to retrieve from system keyring.",
            )
            self.username = get_keyring_password(KEYRING_SERVICE_NAME, "sap_username")

        if not self.password:
            logger.warning(
                "SAP_PASSWORD is not set in environment variables. Attempting to retrieve from system keyring.",
            )
            self.password = get_keyring_password(KEYRING_SERVICE_NAME, "sap_password")


class APIConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        env_prefix="API_",
        case_sensitive=False,
        extra="ignore",
    )

    key: str | None = None
    key_header: str = "X-API-Key"
    base_url: str | None = "http://localhost:8000/api/v1"

    def model_post_init(self, __context) -> None:
        """Post initialization hook to handle keyring API key retrieval."""
        if not self.key:
            logger.warning(
                "API_KEY is not set in environment variables. Attempting to retrieve from system keyring.",
            )
            self.key = get_keyring_password(KEYRING_SERVICE_NAME, "api_key")


class WorkerConfig(BaseModel):
    model_config = SettingsConfigDict(
        env_file=get_env_file(),
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
        env_file=get_env_file(),
        case_sensitive=False,
        extra="ignore",
    )

    env: str = ENV
    api: APIConfig = APIConfig()
    db: DBConfig = DBConfig()
    sap: SAPConfig = SAPConfig()
    worker: WorkerConfig = WorkerConfig()
    keyring_service_name: str = KEYRING_SERVICE_NAME

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
__all__ = ["config"]
