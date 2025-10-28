from pydantic_settings import BaseSettings, SettingsConfigDict
from settings.config import get_env_file


class SAPSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        env_prefix="SAP_",
        case_sensitive=False,
        extra="ignore",
    )

    username: str | None = None
    password: str | None = None
    connection_name: str | None = "SAP 340 Quality"
    window_title: str | None = "SAP Logon 770"
    executable_path: str | None = (
        r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe"
    )

    