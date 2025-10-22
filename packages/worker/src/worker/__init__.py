from worker.logger import logger
from worker.config import config
from worker.core import app


def main():
    logger.info("Starting worker...")
    app.run_worker(concurrency=config.worker.concurrency, name=config.worker.name)


__all__ = ["app"]


if __name__ == "__main__":
    main()
