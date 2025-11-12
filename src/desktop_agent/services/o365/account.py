from typing import TypedDict
from O365 import Account
import logging

logger = logging.getLogger(__name__)


class MSGraphCredentials(TypedDict):
    client_id: str
    client_secret: str
    tenant_id: str
    main_resource: str


def _validate_credentials(credentials: MSGraphCredentials):
    required = ["client_id", "client_secret", "tenant_id", "main_resource"]
    missing = [k for k in required if not credentials.get(k)]

    if missing:
        raise ValueError(f"Missing required credentials: {', '.join(missing)}")

    return True


# Factory function to create and authenticate O365 account
def create_o365_account(credentials: MSGraphCredentials) -> Account:
    _validate_credentials(credentials)

    account = Account(
        credentials=(credentials["client_id"], credentials["client_secret"]),
        tenant_id=credentials["tenant_id"],
        auth_flow_type="credentials",
        main_resource=credentials["main_resource"],
    )

    if not account.is_authenticated:
        logging.info("Account not authenticated. Attempting to authenticate.")
        success = account.authenticate()
        if not success:
            raise ValueError(
                "Failed to authenticate account with provided credentials."
            )

    return account
