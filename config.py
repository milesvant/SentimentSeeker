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
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    LANGUAGES = ['en', 'es']
    REDIS_URL = os.getenv('REDIS_URL')
