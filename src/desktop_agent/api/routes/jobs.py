from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Any
from desktop_agent.worker.core import app


class JobRequest(BaseModel):
    name: str
    kwargs: dict[str, Any]
    queue: str | None = "default"
    priority: int = 0


class JobResponse(BaseModel):
    success: bool
    message: str = "Job {name} deferred successfully."
    job_id: int


router = APIRouter(prefix="/jobs", tags=["Job Queue"])


@router.post(
    "/defer",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=JobResponse,
    description="Defer a job to be executed",
)
async def defer_job(req: JobRequest):
    with app.open():
        job = app.configure_task(req.name).defer(**req.kwargs)

    return {
        "success": True,
        "message": f"Job {req.name} deferred successfully.",
        "job_id": job,
    }
