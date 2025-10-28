from pydantic_settings import BaseSettings, SettingsConfigDict
from settings.config import get_env_file


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

