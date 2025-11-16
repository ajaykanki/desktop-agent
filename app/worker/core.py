import asyncio
import functools
import sys
from typing import Any, Callable, Optional
from app.models import JobResult
from app.config import config
from procrastinate import App, PsycopgConnector, JobContext
from pprint import pprint


# Set event loop policy only on Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


app = App(
    connector=PsycopgConnector(conninfo=config.db.url),
    import_paths=config.worker.import_paths,
)


def post_result(result: JobResult) -> None:
    print("Post task result function!")
    pprint(result.model_dump())


# Use this decorator to define tasks
def task(original_func: Optional[Callable] = None, **kwargs):
    """
    Task middleware to define procrastinate tasks and do something with the result
    """
    def wrap(func: Callable) -> Callable:
        @functools.wraps(func)
        def new_func(*job_args, **job_kwargs) -> Any:
            context: JobContext = job_args[0] if job_args else None

            try:
                result = func(*job_args, **job_kwargs)
                job_result = JobResult(
                    id=context.job.id if context else None,
                    status="succeeded",
                    task_name=context.job.task_name if context else "unknown",
                    worker_name=context.worker_name if context else "unknown",
                    worker_id=context.job.worker_id if context else None,
                    data=result,
                )
                post_result(job_result)
                return result
            except Exception as e:
                # Post error result
                error_object = {
                    "type": type(e).__name__,
                    "message": str(e),
                }
                job_result = JobResult(
                    id=context.job.id if context else None,
                    status="failed",
                    task_name=context.job.task_name if context else "unknown",
                    worker_name=context.worker_name if context else "unknown",
                    worker_id=context.job.worker_id if context else None,
                    data=error_object,
                )
                post_result(job_result)
                # Re-raise the exception to maintain the expected error behavior
                raise

        return app.task(**kwargs)(new_func)

    if original_func is None:
        return wrap

    return wrap(original_func)
