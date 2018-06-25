import os
import yaml
import redis
from datetime import timedelta
from rq import Connection, Worker


class Config(object):
    basedir = os.path.abspath(os.path.dirname(__file__))
    CONFIG_FILE = "%s/flask_config.yaml" % basedir
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as y:
            config_data = yaml.safe_load(y)
            SECRET_KEY = config_data['SECRET_KEY']
    else:
        SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    ADMINS = ['your-email@example.com']
    POSTS_PER_PAGE = 3
    LANGUAGES = ['en', 'es']
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    REDIS_URL = os.environ.get('REDIS_URL')
