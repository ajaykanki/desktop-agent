from fastapi import APIRouter, status, Depends
from ..auth import verify_api_key
from pydantic import BaseModel
from typing import Any
from app.worker.core import app

router = APIRouter()


class JobRequest(BaseModel):
    name: str
    kwargs: dict[str, Any] | None = None
    queue: str | None = None
    priority: int | None = None
    job_options: dict[str, Any] | None = None


class JobResponse(BaseModel):
    success: bool
    message: str = "Job {name} deferred successfully."
    job_id: int


@router.post(
    "/defer",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=JobResponse,
    description="Defer a job to be executed",
)
async def defer_job(req: JobRequest, key: str = Depends(verify_api_key)):
    print(req.model_dump())
    with app.open():
        job_id = app.configure_task(
            name=req.name,
            queue=req.queue,
            priority=req.priority,
            **req.job_options if req.job_options else {},
        ).defer(**req.kwargs)

    return {
        "success": True,
        "job_id": job_id,
        "message": f"Job {req.name} deferred successfully.",
    }
