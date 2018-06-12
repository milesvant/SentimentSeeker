import os
from app import db
from app.models import YoutubeVideoDB
from app.main.youtube.search import youtube_search
from app.main.youtube.youtube_video import Youtube_Video
from rq import get_current_job
from flask import current_app
from topic import create_app


def sort_videos(query, max_results=10):
    """Returns two sorted lists of videos based on a query.

        Args:
            query: A string query.
            max_results: The maximum number of results requested, default is 10.
        Returns:
            Two lists of youtube videos which are the top max_results number of
            videos from a search (through Youtube's API). These results are scored
            based on their captions' sentiment, placed into lists corresponding
            to positive and negative results, sorted, and returned.
    """
    app = create_app()
    app.app_context().push()
    videos = youtube_search(query, max_results)
    i = 1
    for vid in videos:
        # Search for matching entry in database
        db_entry = vid.find_db_entry()
        needs_update = False
        if db_entry is not None:
            vid.from_db_entry(db_entry)
        if vid.caption is None:
            vid.download_sub()
            needs_update = True
        if vid.score is None:
            vid.calculate_sentiment()
            needs_update = True
        if db_entry is None:
            vid.add_to_db()
        elif needs_update:
            db.session.delete(db_entry)
            vid.add_to_db()
            db.session.commit()
        _set_progress(i, max_results)
        _add_video(vid)
        i += 1


def _set_progress(num, max):
    job = get_current_job()
    if job:
        progress = num/max
        job.meta['progress'] = progress
        job.save_meta()
        if progress >= 1.0:
            job.complete = True


def _add_video(video):
    job = get_current_job()
    if job:
        if 'videos' in job.meta.keys():
            job.meta['videos'].append(video.serialize())
        else:
            job.meta['videos'] = [video.serialize()]
