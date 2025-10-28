from desktop_agent.logger import logger
from desktop_agent.worker.core import app, workerConfig


def run_worker():
    logger.info("Starting worker...")
    with app.open():
        try:
            app.schema_manager.apply_schema()
        except Exception:
            logger.error("Schema already applied or failed to apply schema")

    app.run_worker(concurrency=workerConfig.concurrency, name=workerConfig.name)


if __name__ == "__main__":
    run_worker()
