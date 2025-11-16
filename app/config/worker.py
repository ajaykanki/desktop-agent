from pydantic_settings import BaseSettings, SettingsConfigDict
from app.logging import log
from .utils import get_env_file, get_keyring_password


class WorkerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        env_prefix="WORKER_",
        case_sensitive=False,
        extra="ignore",
    )

    concurrency: int = 1
    name: str | None = None
    queues: list[str] | None = None
    import_paths: list[str] = ["tasks"]
    api_key: str | None = None
    network_drive_letter: str | None = "Z:"  # With colon

    def validate_config(self) -> bool:
        if not self.api_key:
            log.error("WORKER_API_KEY is not set in environment variables or keyring.")
            return False

        if not self.network_drive_letter:
            log.error(
                "WORKER_NETWORK_DRIVE_LETTER is not set in environment variables or keyring."
            )
            return False

        return True

    def model_post_init(self, context):
        if self.api_key is None:
            log.warning(
                "WORKER_API_KEY is not set in environment variables. Attempting to retrieve from keyring."
            )
            self.api_key = get_keyring_password("WORKER_API_KEY")

            if not self.validate_config():
                log.error("Invalid configuration. Exiting.")
                exit(1)

        return super().model_post_init(context)
