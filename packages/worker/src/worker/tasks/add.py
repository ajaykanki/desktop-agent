from worker.proc import app


@app.task(name="sum")
def sum(a, b):
    return a + b
