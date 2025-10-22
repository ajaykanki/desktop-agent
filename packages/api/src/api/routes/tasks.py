from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Dict, Any
from procrastinate import App, PsycopgConnector
from api.config import config


class TaskEnqueueRequest(BaseModel):
    name: str
    args: Dict[str, Any]
    queue: str | None = "default"
    priority: int = 0


router = APIRouter(prefix="/tasks", tags=["Task Queue"])

app = App(connector=PsycopgConnector(conninfo=config.db.url))


@router.post("/enqueue", status_code=status.HTTP_202_ACCEPTED)
async def enqueue_task(request: TaskEnqueueRequest):
    with app.open():
        job = app.configure_task(request.name).defer(**request.args)

    return job
