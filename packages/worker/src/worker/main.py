import asyncio
import random
import sys
import time

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from procrastinate import App, PsycopgConnector

app = App(
    connector=PsycopgConnector(
        kwargs={
            "host": "localhost",
            "user": "postgres",
            "password": "password",
        }
    )
)

@app.task(name="sum")
def sum(a, b):
    print(f"Computed {a} + {b} = {a + b}")
    return a + b

def main():
    import logging
    logging.basicConfig(level=logging.INFO)
    app.run_worker(queues=["sum"], name="worker-name")
