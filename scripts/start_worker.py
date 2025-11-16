from app.logging import log
from app.worker.core import app
from app.config import config
import logging

logging.basicConfig(level=logging.DEBUG if config.is_dev else logging.WARNING)


def run_worker():
    log.info("Starting worker...")
    validate_configs()
    apply_schema()
    app.run_worker(
        concurrency=config.worker.concurrency,
        name=config.worker.name,
        queues=config.worker.queues,
    )


def apply_schema():
    with app.open():
        try:
            app.schema_manager.apply_schema()
        except Exception:
            log.warning("Schema already applied or failed to apply schema")


def validate_configs():
    if not config.worker.validate_config():
        log.error("Worker configuration is invalid. Exiting.")
        exit(1)

    if not config.sap.validate_config():
        log.error("SAP configuration is invalid. Exiting.")
        exit(1)


if __name__ == "__main__":
    run_worker()
