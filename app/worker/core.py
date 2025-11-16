import asyncio
import functools
from app.models import JobResult
from app.config import config
from procrastinate import App, PsycopgConnector, JobContext
from pprint import pprint

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


app = App(
    connector=PsycopgConnector(conninfo=config.db.url),
    import_paths=config.worker.import_paths,
)


def post_result(result: JobResult):
    print("Post task result function!")
    pprint(result.model_dump())


# Use this decorator to define tasks
def task(original_func=None, **kwargs):
    def wrap(func):
        def new_func(*job_args, **job_kwargs):
            context: JobContext = job_args[0]
            # Do something before the task is executed
            try:
                result = func(*job_args, **job_kwargs)
                job_result = JobResult(
                    id=context.job.id,
                    status="succeeded",
                    task_name=context.job.task_name,
                    worker_name=context.worker_name,
                    worker_id=context.job.worker_id,
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
                    id=context.job.id,
                    status="failed",
                    task_name=context.job.task_name,
                    worker_name=context.worker_name,
                    worker_id=context.job.worker_id,
                    data=error_object,
                )
                post_result(job_result)
                return result

        wrapped_func = functools.update_wrapper(new_func, func, updated=())
        return app.task(**kwargs)(wrapped_func)

    if not original_func:
        return wrap

    return wrap(original_func)
