"""
    Added celery for task management.
"""

from flask import Flask
from celery import Celery, Task

def celery_init_app(app: Flask) -> Celery:
    """Celery added for task.

    Args:
        app (Flask): Celery for flask.

    Returns:
        Celery: Celery app for running celery task.
    """
    class FlaskTask(Task):
        """Celery task

        Args:
            Task (background_Task): "Celery Added here for sentiment analysis."
        """
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


# celery -A api.celery_app worker --pool=solo -l info