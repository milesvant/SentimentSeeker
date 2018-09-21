web: flask db upgrade; gunicorn topic:app
worker: rq worker -u $REDIS_URL default
