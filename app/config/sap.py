from pydantic_settings import BaseSettings, SettingsConfigDict
from app.logging import log
from .utils import get_env_file, get_keyring_password


class SAPSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        env_prefix="SAP_",
        case_sensitive=False,
        extra="ignore",
    )

    username: str | None = None
    password: str | None = None
    connection_name: str | None = "340 Quality"
    window_title: str | None = "SAP Logon 770"
    executable_path: str | None = (
        r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe"
    )

    def model_post_init(self, context):
        if self.username is None:
            log.warning(
                "SAP_USERNAME is not set in environment variables. Attempting to retrieve from keyring."
            )
            self.username = get_keyring_password("SAP_USERNAME")

        if self.password is None:
            log.warning(
                "SAP_PASSWORD is not set in environment variables. Attempting to retrieve from keyring."
            )
            self.password = get_keyring_password("SAP_PASSWORD")

        return super().model_post_init(context)

    def validate_config(self) -> bool:
        errors = []
        if not self.username:
            errors.append(
                "SAP_USERNAME is not set in environment variables or keyring."
            )

        if not self.password:
            errors.append(
                "SAP_PASSWORD is not set in environment variables or keyring."
            )

        if errors:
            for err in errors:
                log.error(err)

            log.info("Configuration validation failed.")
            return False

        return True
