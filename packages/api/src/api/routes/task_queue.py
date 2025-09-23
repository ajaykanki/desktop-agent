from fastapi import APIRouter, status
from pydantic import BaseModel


class TaskEnqueueRequest(BaseModel):
    name: str
    args: dict[str, any]
    queue: str | None = "default"
    lock: str | None = None
    priority: int = 0


router = APIRouter(prefix="/tasks", tags=["Task Queue"])


@router.post("/enqueue", status_code=status.HTTP_202_ACCEPTED)
async def enqueue_task(request: TaskEnqueueRequest):
    pass
