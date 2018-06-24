import pickle
import numpy as np
from app import db
from app.models import TweetDB, YoutubeVideoDB
from app.models import InitialTrainingDataDB, LogisticRegressionModel
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


def train_logistic_regression(use_db=False):
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
    for entry in InitialTrainingDataDB.query.all():
        data.append(entry.text)
        if entry.positive:
            data_labels.append(1)
        else:
            data_labels.append(-1)
    # If using voted-on videos and tweets, add those as well
    if use_db:
        pass
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
    return log_model, accuracy_score(y_test, y_pred)


def store_logistic_regression(model, accuracy):
    """Stores a trained logistic regression model in the database.

       Args:
            model: A sklearn LogisticRegression object
            accuracy: float between 0 and 1 representing the model's accuracy
    """
    pickled_model = pickle.dumps(model)
    lrmodel = LogisticRegressionModel(model=pickled_model, accuracy=accuracy)
    db.session.add(lrmodel)
    db.session.commit()
