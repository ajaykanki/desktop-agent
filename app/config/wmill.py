from pydantic_settings import BaseSettings, SettingsConfigDict
from app.logging import log
from .utils import get_env_file, get_keyring_password


class WmillSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        env_prefix="WMILL_",
        case_sensitive=False,
        extra="ignore",
    )

    instance_url: str | None = None
    super_admin_token: str | None = None
    base_api_url: str | None = None

    def model_post_init(self, context):
        if self.instance_url is None:
            log.warning("WMILL_INSTANCE_URL is not set in environment variables")

        if self.super_admin_token is None:
            log.warning(
                "WMILL_SUPER_ADMIN_TOKEN is not set in environment variables. Attempting to retrieve from keyring."
            )
            self.super_admin_token = get_keyring_password("WMILL_SUPER_ADMIN_TOKEN")

        if self.instance_url:
            if not self.instance_url.startswith("http://"):
                raise ValueError("WMILL_INSTANCE_URL must start with http://")

            if self.instance_url.endswith("/"):
                self.instance_url = self.instance_url.rstrip("/")

            self.base_api_url = self.instance_url + "/api"
        return super().model_post_init(context)

    def validate_config(self) -> bool:
        errors = []
        if not self.instance_url:
            errors.append("WMILL_INSTANCE_URL is not set in environment variables.")

        if not self.super_admin_token:
            errors.append(
                "WMILL_SUPER_ADMIN_TOKEN is not set in environment variables or keyring."
            )

        if errors:
            for err in errors:
                log.error(err)

            log.info("Configuration validation failed.")
            return False

        return True
