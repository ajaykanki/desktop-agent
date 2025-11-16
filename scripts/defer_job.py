import sys
import os
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.worker.core import app


def defer_job(name: str, args: dict):
    with app.open():
        app.configure_task(name).defer(**args)


if __name__ == "__main__":
    defer_job("add", {"a": 1, "b": 2})
