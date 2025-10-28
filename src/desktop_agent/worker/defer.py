from desktop_agent.worker.core import app

def defer_job(name: str, args: dict):
    with app.open():
        app.configure_task(name).defer(**args)


if __name__ == "__main__":
    defer_job("add", {"a": 1, "b": 2})
