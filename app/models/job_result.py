from pydantic import BaseModel
from typing import Any


class JobResult(BaseModel):
    id: str | int
    worker_id: str | int
    worker_name: str | None
    task_name: str
    status: str
    data: dict[str, Any]
