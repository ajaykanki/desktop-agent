from pydantic_settings import BaseSettings, SettingsConfigDict
from settings import get_env_file, get_keyring_password
from logger import logger


class WorkerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        env_prefix="WORKER_",
        case_sensitive=False,
        extra="ignore",
    )

    concurrency: int = 1
    name: str | None = None
    queues: list[str] | str = "sap"
    import_paths: list[str] = ["tasks"]
    api_key: str | None = None

    def model_post_init(self, context):
        if self.api_key is None:
            logger.warning(
                "WORKER_API_KEY is not set in environment variables. Attempting to retrieve from keyring."
            )
            self.api_key = get_keyring_password("WORKER_API_KEY")

        return super().model_post_init(context)
