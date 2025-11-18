from procrastinate import JobContext
from .sap import create_sales_orders
from app.worker.core import task


@task(name="add", queue="sap", lock="sap", pass_context=True)
def add(context: JobContext, a: int, b: int):
    print("Adding {a} and {b}".format(a=a, b=b))
    return {
        "a": a,
        "b": b,
        "result": a + b,
    }
