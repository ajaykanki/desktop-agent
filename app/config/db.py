from pydantic_settings import BaseSettings, SettingsConfigDict
from .utils import get_keyring_password, get_env_file
from app.logging import log


class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        env_prefix="DB_",
        case_sensitive=False,
        extra="ignore",
    )
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str | None = None
    name: str = "postgres"
    url: str | None = None

    def model_post_init(self, context):
        # Check if DB_URL was provided in env
        if self.url:
            return super().model_post_init(context)

        # Construct DB_URL
        if self.password is None:
            log.warning(
                "DB_PASSWORD is not set in environment variables. Attempting to retrieve from keyring."
            )
            self.password = get_keyring_password("DB_PASSWORD")
            if not self.password:
                return super().model_post_init(context)

        self.url = f"postgres://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

        return super().model_post_init(context)
