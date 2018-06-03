from app.main.youtube.search import youtube_search
from app.main.youtube.nlp import sentiment_list
from app.main.youtube.youtubedl import download_sub

from oauth2client.tools import argparser


def sort(query):
    my_videos = youtube_search(query, max_results=10)
    captions = {}
    for vid in my_videos.keys():
        captions[vid] = download_sub(vid)
    return my_videos, sentiment_list(captions)
