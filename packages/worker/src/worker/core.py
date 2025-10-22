import asyncio
import logging
from worker.config import config
from procrastinate import App, PsycopgConnector

logging.basicConfig(level=logging.DEBUG if config.is_dev else logging.INFO)
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = App(
    connector=PsycopgConnector(conninfo=config.db.url),
    import_paths=config.worker.import_paths,
)
