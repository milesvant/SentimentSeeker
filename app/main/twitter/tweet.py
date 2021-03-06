import os
import re
import pickle
from textblob import TextBlob
from app import db
from app.models import TweetDB
from flask import current_app


class Tweet:
    """A class representing a Tweet.

       Attributes:
            name: The author of this tweet.
            text: The text of this tweet.
            id: The id of this tweet.
            score: This tweet's sentiment score
    """

    def __init__(self, name, text, id, score=None):
        self.name = name
        self.text = text
        self.id = int(id)
        self.score = score

    def __repr__(self):
        return "<Tweet name:{} text:{} id: {} score:{}>".format(
            self.name,
            self.text,
            self.id,
            self.score)

    def calculate_sentiment(self):
        """Calculates the sentiment score for this Tweet"""
        tb = TextBlob(self.text)
        if tb.sentiment.polarity > 0:
            self.score = (tb.sentiment.polarity +
                          tb.sentiment.subjectivity)
        else:
            self.score = (tb.sentiment.polarity -
                          tb.sentiment.subjectivity)

    def add_to_db(self):
        """Adds this Tweet to the app (SQL) database"""
        twt = TweetDB(name=self.name,
                      text=self.text,
                      twitter_id=self.id,
                      score=self.score)
        db.session.add(twt)
        db.session.commit()

    def find_db_entry(self):
        """Searches app (SQL) database to see if a matching entry exists.

            Returns:
                First database entry whose id matches this Tweet.
        """
        db_entry = TweetDB.query.filter_by(twitter_id=str(self.id)).first()
        if db_entry is not None:
            return db_entry

    def from_db_entry(self, db_entry):
        """Creates a Youtube_Video object representation of a database
            entry."""
        self.text = db_entry.text
        self.name = db_entry.name
        self.id = db_entry.twitter_id
        self.score = db_entry.score

    def serialize(self):
        """Returns a serialized version of the information needed to
            progressively load video results onto the results page."""
        return {
            'name': self.name,
            'text': self.text,
            'id': self.id,
            'score': self.score,
        }
