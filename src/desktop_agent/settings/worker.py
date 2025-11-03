from pydantic_settings import BaseSettings, SettingsConfigDict
from desktop_agent.settings import get_env_file, get_keyring_password
from desktop_agent.logger import logger


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

    def validate_config(self) -> bool:
        if not self.api_key:
            logger.error(
                "WORKER_API_KEY is not set in environment variables or keyring."
            )
            return False

        return True

    def model_post_init(self, context):
        if self.api_key is None:
            logger.warning(
                "WORKER_API_KEY is not set in environment variables. Attempting to retrieve from keyring."
            )
            self.api_key = get_keyring_password("WORKER_API_KEY")

            if not self.validate_config():
                logger.error("Invalid configuration. Exiting.")
                exit(1)

        return super().model_post_init(context)

config = WorkerSettings()
