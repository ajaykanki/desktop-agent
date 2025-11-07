from pydantic import BaseModel
from typing import Any


class JobResult(BaseModel):
    id: str
    worker_id: str
    worker_name: str
    task_name: str
    status: str
    data: dict[str, Any]
