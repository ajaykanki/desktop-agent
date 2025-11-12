from desktop_agent.logger import logger
from desktop_agent.worker.core import app
from desktop_agent.settings import config


def run_worker():
    logger.info("Starting worker...")
    with app.open():
        try:
            app.schema_manager.apply_schema()
        except Exception:
            logger.warning("Schema already applied or failed to apply schema")

    if not config.worker.validate_config():
        logger.error("Worker configuration is invalid. Exiting.")
        exit(1)

    if not config.sap.validate_config():
        logger.error("SAP configuration is invalid. Exiting.")
        exit(1)

    app.run_worker(
        concurrency=config.worker.concurrency,
        name=config.worker.name,
        queues=config.worker.queues,
    )


if __name__ == "__main__":
    run_worker()
