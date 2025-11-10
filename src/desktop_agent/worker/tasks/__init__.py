from .sap import create_sales_orders
from desktop_agent.worker.core import task
from procrastinate import JobContext


@task(name="add", queue="sap", lock="sap", pass_context=True)
def add(context: JobContext, a: int, b: int):
    print("Adding {a} and {b}".format(a=a, b=b))
    return {
        "a": a,
        "b": b,
        "result": a + b,
    }


__all__ = ["add", "create_sales_orders"]
