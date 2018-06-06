import os
import re
import youtube_dl
from textblob import TextBlob


class Youtube_Video:
    """A class representing a Youtube Video with a caption track.

       Attributes:
            videoid: The Youtube videoId of this video.
            name: The name of this video.
            caption: A string (plaintext english) representation of the caption
                track of this video.
            score: This Youtube Video's sentiment score
    """

    def __init__(self, videoid=None, name=None):
        self.videoid = videoid
        self.name = name
        self.caption = None
        self.score = 0

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
