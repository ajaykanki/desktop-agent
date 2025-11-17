import asyncio
from app.config import config
from app.logging import log
from app.email.wmill_client import Windmill
from app.email.monitor import EmailMonitor


def validate_configs():
    if not config.o365.validate_config():
        log.error("O365 configuration is invalid. Exiting.")
        exit(1)

    if not config.wmill.validate_config():
        log.error("WMILL configuration is invalid. Exiting.")
        exit(1)

    return


async def start_email_monitor():
    validate_configs()
    wmill_client = Windmill(
        instance_url=config.wmill.instance_url,
        super_admin_token=config.wmill.super_admin_token,
    )

    monitor = EmailMonitor(config.o365, wmill_client)
    await monitor.start()


if __name__ == "__main__":
    asyncio.run(start_email_monitor())
