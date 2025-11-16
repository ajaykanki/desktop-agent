import os
import keyring
from app.logging import log

ENV = os.getenv("ENV", "dev").lower()
PRODUCTION = ["prod", "production"]
KEYRING_SERVICE_NAME = "desktop-agent"


def get_env_file():
    """Get the appropriate environment file based on the current environment."""
    env_file = ".env" if ENV in PRODUCTION else f".env.{ENV}"
    return env_file


def get_keyring_password(
    key_name: str, service_name: str = KEYRING_SERVICE_NAME
) -> str | None:
    """
    Safely retrieve password from system keyring.

    Args:
        service_name: The name of the service to retrieve from keyring
        key_name: The key name to retrieve from keyring

    Returns:
        The password string if found, None otherwise
    """
    try:
        password = keyring.get_password(service_name, key_name)
        if password is None:
            log.debug(f"No keyring entry found for {key_name}")

        return password
    except Exception as e:
        log.warning(f"Failed to retrieve {key_name} from keyring: {e}")
        return None
