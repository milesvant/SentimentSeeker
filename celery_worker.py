import os
from app import celery, create_app
from app.ml.ml_task import run_update_sentiment
from celery import Celery
from celery.schedules import crontab


def create_celery(app):
    celery = Celery(app.import_name,
                    backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['REDIS_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


flask_app = create_app()
flask_app.app_context().push()
celery = create_celery(flask_app)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls reverse_messages every 10 seconds.
    sender.add_periodic_task(60.0,
                             run_update_sentiment,
                             name='run_update_sentiment every 60')
