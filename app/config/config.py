from .api import APISettings
from .db import DBSettings
from .wmill import WmillSettings
from .worker import WorkerSettings
from .o365 import O365Settings
from .sap import SAPSettings
from .utils import KEYRING_SERVICE_NAME, PRODUCTION, ENV
from app.logging import log
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
        case_sensitive=False,
        extra="ignore",
    )
    env: str = ENV
    api: APISettings = APISettings()
    db: DBSettings = DBSettings()
    sap: SAPSettings = SAPSettings()
    worker: WorkerSettings = WorkerSettings()
    o365: O365Settings = O365Settings()
    wmill: WmillSettings = WmillSettings()
    keyring_service_name: str = KEYRING_SERVICE_NAME

    @property
    def is_dev(self) -> bool:
        return self.env in ["dev", "development"]

    @property
    def is_prod(self) -> bool:
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
                log.error(err)

            log.info("Configuration validation failed.")
            return False

        return True


def _load_config() -> Config:
    config = Config()
    if not config.validate_config():
        log.error("Invalid configuration. Exiting.")
        exit(1)

    return config


config = _load_config()
