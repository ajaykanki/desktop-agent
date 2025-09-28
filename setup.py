import keyring
import getpass
from loguru import logger as log

KEYRING_SERVICE = "desktop-agent"


def setup_credentials():
    """
    Function to get user credentials and store them in the system keyring
    """
    log.info("Setting up credentials for desktop-agent...")

    api_key = getpass.getpass("Enter API key: ")
    keyring.set_password(KEYRING_SERVICE, "api_key", api_key)

    db_password = getpass.getpass("Enter database password: ")
    keyring.set_password(KEYRING_SERVICE, "db_password", db_password)
    log.info("Database password stored securely.")

    sap_username = input("Enter SAP username: ")
    keyring.set_password(KEYRING_SERVICE, "sap_username", sap_username)
    log.info("SAP username stored securely.")

    sap_password = getpass.getpass("Enter SAP password: ")
    keyring.set_password(KEYRING_SERVICE, "sap_password", sap_password)
    log.info("SAP password stored securely.")

    log.success("All credentials have been stored securely in the system keyring.")

if __name__ == "__main__":
    setup_credentials()
