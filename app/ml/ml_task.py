import glob
from app import celery, db
from app.models import LogisticRegressionModel, InitialTrainingDataDB
from flask import current_app
from celery.task.base import periodic_task
from config import Config
from app.ml.sentiment_logistic_regression import train_logistic_regression
from app.ml.sentiment_logistic_regression import store_logistic_regression
from datetime import timedelta


def add_training_data_to_db():
    for file in glob.glob('./training_data/pos/*.txt'):
        with open(file) as f:
            text = f.read()
            itdb = InitialTrainingDataDB(text=f.read(), positive=True)
            db.session.add(itdb)
            db.session.commit()
    for file in glob.glob('./training_data/neg/*.txt'):
        with open(file) as f:
            itdb = InitialTrainingDataDB(text=f.read(), positive=False)
            db.session.add(itdb)
            db.session.commit()


def reset_use_me():
    """Set the use_me column for the best classifier to True and False for all
        other classifiers in the db"""
    for model in LogisticRegressionModel.query.all():
        model.use_me = False
    if len(LogisticRegressionModel.query.all()) != 0:
        max(LogisticRegressionModel.query.all()).use_me = True


@periodic_task(run_every=timedelta(seconds=15))
def run_update_sentiment(use_db=False):
    """Trains a new logistic regression model"""
    # make sure at least initial training data exists in the database
    if len(InitialTrainingDataDB.query.all()) is 0:
        add_training_data_to_db()
    model, accuracy = train_logistic_regression(use_db)
    store_logistic_regression(model, accuracy)
    reset_use_me()
    return
