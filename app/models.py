from datetime import datetime
from app import db
from time import time


class YoutubeVideoDB(db.Model):
    """Database model for a Youtube Video"""
    id = db.Column(db.Integer, primary_key=True)
    videoid = db.Column(db.String(12), index=True, unique=True)
    title = db.Column(db.String(100), index=True, unique=False)
    caption = db.Column(db.String(10000), unique=False, default=None)
    score = db.Column(db.Integer, unique=False, default=None)
    correct = db.Column(db.Boolean, default=None)

    def __repr__(self):
        return '<Youtube Video id:{} title:{} score:{}>'.format(
            self.videoid, self.title, self.score)


class TweetDB(db.Model):
    """Database model for a Tweet"""
    id = db.Column(db.Integer, primary_key=True)
    twitter_id = db.Column(db.BigInteger, unique=True)
    name = db.Column(db.String(12), index=True, unique=False)
    text = db.Column(db.String(280), unique=False)
    score = db.Column(db.Integer, unique=False, default=None)
    correct = db.Column(db.Boolean, default=None)

    def __repr__(self):
        return '<Tweet tweeter:{} content:{} score:{}>'.format(
            self.tweeter, self.content. self.score)
