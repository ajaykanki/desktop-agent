import os
import keyring
from shared import KEYRING_SERVICE, ConfigBase
from loguru import logger
from pathlib import Path
from pydantic_settings import SettingsConfigDict, BaseSettings

env = os.getenv("ENV", "dev")
env_file = f".env.{env}" if env != "production" else ".env"
env_path = Path(env_file)


class SAPConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file,
        env_prefix="SAP_",
        case_sensitive=False,
        extra="ignore",
    )

    username: str | None = None
    password: str | None = None
    connection_name: str | None = "SAP 340 Quality"
    window_title: str = "SAP Logon 770"
    automation_base_path: str = r"Z:"
    prefix_id: str = r"wnd[0]/usr"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.username:
            logger.warning(
                "SAP username is not set in environment variables. Retrieving from system keyring."
            )
            self.username = keyring.get_password(KEYRING_SERVICE, "sap_username")

        if not self.password:
            logger.warning(
                "SAP password is not set in environment variables. Retrieving from system keyring."
            )
            self.password = keyring.get_password(KEYRING_SERVICE, "sap_password")


class WorkerConfig(ConfigBase):
    sap: SAPConfig = SAPConfig()

    def validate_config(self):
        if not self.sap.connection_name:
            logger.error("SAP connection name is not set in environment variables.")
            self.error = True

        if not self.sap.username:
            logger.error("SAP username is not set in environment variables or keyring.")
            self.error = True

        if not self.sap.password:
            logger.error("SAP password is not set in environment variables or keyring.")
            self.error = True

        super().validate_config()


config = WorkerConfig()
config.validate_config()
