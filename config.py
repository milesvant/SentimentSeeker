import os
import yaml
import redis
from rq import Connection, Worker

CONFIG_FILE = "flask_config.yaml"
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    with open(CONFIG_FILE) as y:
        config_data = yaml.safe_load(y)
        SECRET_KEY = config_data['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    REDIS_URL = 'redis://redis:6379/0'
    ADMINS = ['your-email@example.com']
    POSTS_PER_PAGE = 3
    LANGUAGES = ['en', 'es']
