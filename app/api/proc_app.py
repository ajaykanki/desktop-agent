"""This procrastinate app is needed just for deferring jobs in the right queue with right lock. Do not use this app to define your tasks. You must only declare your tasks in this file.

Note: All the tasks must be first declared here with appropriate locks and queues, and their definition in the worker.tasks module
"""

import asyncio
import sys
from typing import Any
from procrastinate import App, PsycopgConnector, JobContext
from app.config import config

# Set event loop policy only on Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = App(connector=PsycopgConnector(conninfo=config.db.url))


@app.task(
    name="add",
    queue="sap",
    lock="sap",
    pass_context=True,
)
def add(context: JobContext, a: int, b: int): ...


@app.task(
    name="create_sales_orders",
    queue="sap",
    lock="sap",
    pass_context=True,
)
def create_sales_orders(
    context: JobContext,
    po_working_path: str,
    va01_details: dict[str, Any],
    screen_order: list[dict[str, Any]],
): ...
