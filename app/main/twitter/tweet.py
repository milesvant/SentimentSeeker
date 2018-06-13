import os
import re
from textblob import TextBlob
from app import db
from app.models import Tweet
from flask import current_app


class Tweet:
    """
    """

    def __init__(self, name, text, url, score=None):
        self.name = name
        self.text = text
        self.url = url
        self.score = score

    def __repr__(self):
        return "<Tweet name:{} text:{} url:{} score:{}>".format(self.name,
                                                                self.text,
                                                                self.url,
                                                                self.score)
