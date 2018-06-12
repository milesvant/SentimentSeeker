import os
import re
import youtube_dl
from textblob import TextBlob
from app import db
from app.models import YoutubeVideoDB
from flask import current_app


class Youtube_Video:
    """A class representing a Youtube Video with a caption track.

       Attributes:
            videoid: The Youtube videoId of this video.
            name: The name of this video.
            caption: A string (plaintext english) representation of the caption
                track of this video.
            score: This Youtube Video's sentiment score
    """

    def __init__(self, videoid=None, title=None, caption=None, score=None):
        self.videoid = videoid
        self.title = title
        self.caption = caption
        self.score = score

    @staticmethod
    def ttml_to_plaintext(caption):
        """Converts text from ttml to plaintext.

            Args:
                caption: string of a caption track in the ttml format.
            Returns:
                caption track in plaintext (without any XML tags).
        """
        caption = re.sub("<([^>])+>", "", caption)
        caption = re.sub("&#39;", "\'", caption)
        caption = re.sub("( |)\[([a-z]|[A-Z])+\]", "", caption)
        caption = re.sub("\n", " ", caption)
        return caption

    def download_sub(self):
        """Downloads a caption track for this Youtube video."""
        DOWNLOADS = "%s/downloads" % os.path.abspath(os.path.dirname(__file__))
        ydl_opts = {
            'skip_download': True,  # only download captions, not video
            'subtitleslangs': 'en',
            'writeautomaticsub': True,  # use auto captions only
            'subtitleslangs': ['en'],
            'subtitlesformat': 'ttml',
            'outtmpl': '%s/%s' % (DOWNLOADS, self.videoid),  # format: videoid.en.ttml
            'nocheckcertificate': True,
            'quiet': True,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(["https://www.youtube.com/watch?v=%s" % self.videoid])
        caption = open("%s/%s.en.ttml" % (DOWNLOADS, self.videoid)).read()
        os.system("rm -- %s/%s.en.ttml" % (DOWNLOADS, self.videoid))
        self.caption = self.ttml_to_plaintext(caption)

    def calculate_sentiment(self):
        """Calculates the sentiment score for this Youtube Video"""
        if self.caption is not None:
            tb = TextBlob(self.caption)
            self.score = (tb.sentiment.polarity * tb.sentiment.subjectivity)

    def add_to_db(self):
        """Adds this Youtube Video to the app (SQL) database if its videoid and
            title are valid."""
        if self.videoid is not None and self.title is not None:
            vid = YoutubeVideoDB(videoid=self.videoid, title=self.title,
                                 caption=self.caption, score=self.score)
            db.session.add(vid)
            db.session.commit()

    def find_db_entry(self):
        """Searches app (SQL) database to see if a matching entry exists.

            Returns:
                First database entry whose videoid and title match this Youtube_Video.
        """
        db_entry = YoutubeVideoDB.query.filter_by(videoid=self.videoid).first()
        if db_entry is not None and db_entry.title == self.title:
            return db_entry
        else:
            return None

    def from_db_entry(self, db_entry):
        """Creates a Youtube_Video object representation of a database entry."""
        self.videoid = db_entry.videoid
        self.title = db_entry.title
        self.caption = db_entry.caption
        self.score = db_entry.score

    def serialize(self):
        return {
            'videoid': self.videoid,
            'title': self.title,
            'score': self.score,
        }
