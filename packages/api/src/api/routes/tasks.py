from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Dict, Any


class TaskEnqueueRequest(BaseModel):
    name: str
    args: Dict[str, Any]
    queue: str | None = "default"
    priority: int = 0


router = APIRouter(prefix="/tasks", tags=["Task Queue"])


@router.post("/enqueue", status_code=status.HTTP_202_ACCEPTED)
async def enqueue_task(request: TaskEnqueueRequest):
    pass
