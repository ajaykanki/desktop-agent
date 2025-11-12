from desktop_agent.logger import logger
from pydantic_settings import BaseSettings, SettingsConfigDict
from .constants import get_env_file, ENV, KEYRING_SERVICE_NAME, PRODUCTION
from .api import APISettings
from .db import DBSettings
from .sap import SAPSettings
from .worker import WorkerSettings
from .o365 import O365Settings
from .wmill import WmillSettings


class GlobalConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_env_file(),
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
        # DB_PASSWORD is mandatory to at least start the api server.
        if not self.db.password:
            errors.append("DB_PASSWORD is not set in environment variables or keyring.")

        if errors:
            for err in errors:
                logger.error(err)

            logger.info("Configuration validation failed.")
            return False

        return True


def _load_config() -> GlobalConfig:
    config = GlobalConfig()

    if not config.validate_config():
        logger.error("Invalid configuration. Exiting.")
        exit(1)

    return config
