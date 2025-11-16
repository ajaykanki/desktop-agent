from pydantic_settings import BaseSettings, SettingsConfigDict
from .utils import get_env_file


class APISettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        env_prefix="API_",
        case_sensitive=False,
        extra="ignore",
    )

    host: str = "0.0.0.0"
    port: int = 8000
    key_header: str = "X-API-KEY"
    prefix: str = "/api"

    title: str = "Desktop Worker Agent API"
    version: str = "0.1.0"
    description: str = "A desktop worker agent to execute tasks that require a GUI"
