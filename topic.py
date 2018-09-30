from app import create_app, db
from app.models import YoutubeVideoDB

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'YoutubeVideoDB': YoutubeVideoDB}


@app.cli.command()
def run_worker():
    redis_url = app.config['REDIS_URL']
    redis_connection = redis.from_url(redis_url)
    with Connection(redis_connection):
        worker = Worker(app.config['QUEUES'])
        worker.work()
