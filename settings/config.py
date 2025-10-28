import os
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV = os.getenv("ENV", "dev").lower()
PRODUCTION = ["prod", "production"]
KEYRING_SERVICE_NAME = "desktop-agent"


def get_env_file():
    """Get the appropriate environment file based on the current environment."""
    env_file = ".env" if ENV in PRODUCTION else f".env.{ENV}"
    return env_file


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        case_sensitive=False,
        extra="ignore",
    )

    env: str = ENV
    keyring_service_name: str = KEYRING_SERVICE_NAME

    @property
    def is_dev(self) -> bool:
        return self.env in ["dev", "development"]

    @property
    def is_prod(self) -> bool:
        return self.env in PRODUCTION
