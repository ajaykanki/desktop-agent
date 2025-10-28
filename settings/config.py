from logger import logger
from pydantic_settings import BaseSettings, SettingsConfigDict
from settings import get_env_file, ENV, KEYRING_SERVICE_NAME, PRODUCTION
from settings.api import APISettings
from settings.db import DBSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        case_sensitive=False,
        extra="ignore",
    )

    env: str = ENV
    api: APISettings = APISettings()
    db: DBSettings = DBSettings()
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
                logger.error(err)

            logger.info("Configuration validation failed.")
            return False

        return True


def _load_config() -> Settings:
    config = Settings()

    if not config.validate_config():
        logger.error("Invalid configuration. Exiting.")
        exit(1)

    return config


config = _load_config()
