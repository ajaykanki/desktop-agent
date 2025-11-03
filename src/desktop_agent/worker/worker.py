from desktop_agent.logger import logger
from desktop_agent.worker.core import app
from desktop_agent.settings import worker_config
from desktop_agent.settings import sap_config


def run_worker():
    logger.info("Starting worker...")
    with app.open():
        try:
            app.schema_manager.apply_schema()
        except Exception:
            logger.error("Schema already applied or failed to apply schema")

    is_ok = sap_config.validate_config()

    if not is_ok:
        logger.error("SAP configuration is invalid. Exiting.")
        exit(1)

    app.run_worker(
        concurrency=worker_config.concurrency,
        name=worker_config.name,
        queues=worker_config.queues,
    )


if __name__ == "__main__":
    run_worker()
