from desktop_agent.worker.core import task


@task(name="add")
def add(a: int, b: int) -> int:
    print("Adding numbers...", a, b)
    return a + b
