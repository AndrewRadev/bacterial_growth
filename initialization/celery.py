import os

from celery import Celery, Task


def init_celery(app):
    """
    Main entry point of the module.

    The redis config defaults to port ``6379`` of ``localhost`` to match the
    one used in the "services" docker image. This can be overridden by two
    environment variables:

    * ``REDIS_HOST``
    * ``REDIS_PORT``
    """
    class AppTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = os.getenv('REDIS_PORT', '6379')

    redis_url = f"redis://{redis_host}:{redis_port}/0"

    celery_app = Celery(app.name, task_cls=AppTask)
    celery_app.config_from_object({
        'broker_url':         redis_url,
        'result_backend':     redis_url,
        'task_ignore_result': True,
    })
    celery_app.set_default()
    app.extensions["celery"] = celery_app

    return app
