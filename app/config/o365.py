from pydantic_settings import BaseSettings, SettingsConfigDict
from app.logging import log
from .utils import get_env_file, get_keyring_password


class O365Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        env_prefix="O365_",
        case_sensitive=False,
        extra="ignore",
    )

    client_id: str | None = None
    client_secret: str | None = None
    tenant_id: str | None = None
    main_resource: str | None = None

    def model_post_init(self, context):
        if self.client_id is None:
            log.warning(
                "O365_CLIENT_ID is not set in environment variables. Attempting to retrieve from keyring."
            )
            self.client_id = get_keyring_password("O365_CLIENT_ID")

        if self.client_secret is None:
            log.warning(
                "O365_CLIENT_SECRET is not set in environment variables. Attempting to retrieve from keyring."
            )
            self.client_secret = get_keyring_password("O365_CLIENT_SECRET")

        if self.tenant_id is None:
            log.warning(
                "O365_TENANT_ID is not set in environment variables. Attempting to retrieve from keyring."
            )
            self.tenant_id = get_keyring_password("O365_TENANT_ID")

        if self.main_resource is None:
            log.warning(
                "O365_MAIN_RESOURCE is not set in environment variables. Attempting to retrieve from keyring."
            )
            self.main_resource = get_keyring_password("O365_MAIN_RESOURCE")

        return super().model_post_init(context)

    def validate_config(self) -> bool:
        errors = []
        if not self.client_id:
            errors.append(
                "O365_CLIENT_ID is not set in environment variables or keyring."
            )

        if not self.client_secret:
            errors.append(
                "O365_CLIENT_SECRET is not set in environment variables or keyring."
            )

        if not self.tenant_id:
            errors.append(
                "O365_TENANT_ID is not set in environment variables or keyring."
            )

        if not self.main_resource:
            errors.append(
                "O365_MAIN_RESOURCE is not set in environment variables or keyring."
            )

        if errors:
            for err in errors:
                log.error(err)

            log.info("Configuration validation failed.")
            return False

        return True
