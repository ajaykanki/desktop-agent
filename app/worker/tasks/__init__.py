from procrastinate import JobContext
from .sap import create_sales_orders
from app.worker.core import task
import time


@task(name="add", queue="sap", pass_context=True)
def add(context: JobContext, a: int, b: int):
    print("Adding {a} and {b}".format(a=a, b=b))
    print("Waiting for 20 seconds")
    time.sleep(20)
    print("Done waiting")
    return {
        "a": a,
        "b": b,
        "result": a + b,
    }
