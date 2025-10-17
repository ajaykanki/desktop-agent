from procrastinate import App, PsycopgConnector
from worker.config import config
import asyncio
import logging

logging.basicConfig(level=logging.DEBUG)
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = App(
    connector=PsycopgConnector(conninfo=config.db.url),
    import_paths=config.worker.import_paths,
)
