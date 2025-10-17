from worker.core import app
from worker.config import config


def main():
    app.run_worker(concurrency=config.worker.concurrency, name=config.worker.name)


__all__ = ["app"]


if __name__ == "__main__":
    main()
