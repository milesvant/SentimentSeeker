from app.ml.sentiment_logistic_regression import train_logistic_regression
from app.ml.sentiment_logistic_regression import store_logistic_regression
from app.ml.sentiment_logistic_regression import reset_use_me
from datetime import timedelta
from rq import get_current_job
from topic import create_app


def run_update_sentiment(use_db=True):
    """Trains a new logistic regression model"""
    create_app().app_context().push()
    # make sure at least initial training data exists in the database
    model, accuracy, vectorizer = train_logistic_regression(use_db)
    store_logistic_regression(model, accuracy, vectorizer)
    reset_use_me()
    return
