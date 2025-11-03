import asyncio
import functools
import logging
from desktop_agent.settings import config, worker_config
from procrastinate import App, PsycopgConnector

logging.basicConfig(level=logging.DEBUG if config.is_dev else logging.INFO)
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


app = App(
    connector=PsycopgConnector(conninfo=config.db.url),
    import_paths=worker_config.import_paths,
)


def after_task(result):
    print(
        "Task executed successfully. This is the after task functio. The result returned by the task is:",
        result,
    )


# Use this decorator to define tasks
def task(original_func=None, **kwargs):
    def wrap(func):
        def new_func(*job_args, **job_kwargs):
            # Do something before the task is executed
            result = func(*job_args, **job_kwargs)
            # Do something after the task is executed
            after_task(result)
            return result

        wrapped_func = functools.update_wrapper(new_func, func, updated=())
        return app.task(**kwargs)(wrapped_func)

    if not original_func:
        return wrap

    return wrap(original_func)
