<<<<<<< HEAD
from app import app, db
from app.models import User, Post, YoutubeVideoDB
=======
from app import create_app, db
from app.models import User, Post, YoutubeVideoDB, Task

app = create_app()
>>>>>>> progress-bar


@app.shell_context_processor
def make_shell_context():
<<<<<<< HEAD
    return {'db': db, 'User': User, 'Post': Post, 'YVDB': YoutubeVideoDB}
=======
    return {'db': db, 'User': User, 'Post': Post, 'YoutubeVideoDB': YoutubeVideoDB, 'Task': Task}


@app.cli.command()
def run_worker():
    redis_url = app.config['REDIS_URL']
    redis_connection = redis.from_url(redis_url)
    with Connection(redis_connection):
        worker = Worker(app.config['QUEUES'])
        worker.work()
>>>>>>> progress-bar
