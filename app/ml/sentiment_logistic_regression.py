import pickle
import glob
import numpy as np
from app import db
from app.models import TweetDB, YoutubeVideoDB
from app.models import InitialTrainingDataDB, LogisticRegressionModel
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


def train_logistic_regression(use_db=True):
    """Trains a logistic regression model using the inital training data
        (online movie reviews) as well as videos and tweets in the database
        (if wanted).

        Args:
            use_db: If True then the model will be trained using voted-on
                tweets and youtube videos in the database.
        Returns:
            A trained logistic regression model and its respective accuracy
                score
    """
    data = []
    data_labels = []
    # Add initial training data to the list of data and labels
    for file in glob.glob('./training_data/pos/*.txt'):
        with open(file) as f:
            text = f.read()
            data.append(text)
            data_labels.append(1)
    for file in glob.glob('./training_data/neg/*.txt'):
        with open(file) as f:
            text = f.read()
            data.append(text)
            data_labels.append(-1)
    # If using voted-on videos and tweets, add those as well
    if use_db:
        voted_on_videos = YoutubeVideoDB.query.filter(
            YoutubeVideoDB.correct.isnot(None))
        for video in voted_on_videos:
            data.append(video.caption)
            if video.correct is True and video.score <= 0:
                data_labels.append(-1)
            elif video.correct is True and video.score > 0:
                data_labels.append(1)
            elif video.correct is False and video.score <= 0:
                data_labels.append(1)
            elif video.correct is False and video.score > 0:
                data_labels.append(-1)
        voted_on_tweets = TweetDB.query.filter(TweetDB.correct.isnot(None))
        for tweet in voted_on_tweets:
            data.append(tweet.text)
            if tweet.correct is True and tweet.score <= 0:
                data_labels.append(-1)
            elif tweet.correct is True and tweet.score > 0:
                data_labels.append(1)
            elif tweet.correct is False and tweet.score <= 0:
                data_labels.append(1)
            elif tweet.correct is False and tweet.score > 0:
                data_labels.append(-1)
    vectorizer = CountVectorizer(analyzer='word', lowercase=False,)
    features = vectorizer.fit_transform(data)
    features_nd = features.toarray()
    # train logistic regression
    X_train, X_test, y_train, y_test = train_test_split(
        features_nd,
        data_labels,
        train_size=0.80,
        random_state=1234)
    log_model = LogisticRegression()
    log_model = log_model.fit(X=X_train, y=y_train)
    y_pred = log_model.predict(X_test)
    # Score accuracy then return model and accuracy
    return log_model, accuracy_score(y_test, y_pred), vectorizer


def store_logistic_regression(model, accuracy, vectorizer):
    """Stores a trained logistic regression model in the database.

       Args:
            model: A sklearn LogisticRegression object
            accuracy: float between 0 and 1 representing the model's accuracy
    """
    pickled_model = pickle.dumps(model)
    pickled_vec = pickle.dumps(vectorizer)
    lrmodel = LogisticRegressionModel(
        model=pickled_model, accuracy=accuracy, vectorizer=pickled_vec)
    db.session.add(lrmodel)
    db.session.commit()


def reset_use_me():
    """Delete all but the best LogisticRegressionModel in the db"""
    if len(LogisticRegressionModel.query.all()) != 0:
        best_model = max(LogisticRegressionModel.query.all())
        for model in LogisticRegressionModel.query.all():
            if model != best_model:
                db.session.delete(model)
                db.session.commit()
