import os
from app import db
from app.models import YoutubeVideoDB
from app.main.youtube.search import youtube_search
from app.main.youtube.youtube_video import Youtube_Video
from rq import get_current_job
from topic import create_app


def sort_videos(query):
    """Takes a query and searches YouTube's API for a list of videos matching
        that query, then downloads their captions and calculates their
        sentiment scores. Run asynchronously through Redis Queue.

        Args:
            query: A string query.
            max_results: The maximum number of results requested, default is
                10.
    """
    # give the Redis Queue job a valid Flask application context.
    create_app().app_context().push()
    videos = youtube_search(query, 10)
    max_results = len(videos)
    i = 1
    for vid in videos:
        # Search for matching entry in database
        db_entry = vid.find_db_entry()
        needs_update = False
        if db_entry is not None:
            # replace video with db entry if one exists
            vid.from_db_entry(db_entry)
        if vid.caption is None:
            # download caption if neccesary
            try:
                vid.download_sub()
            except FileNotFoundError:
                i += 1
                continue
            needs_update = True
        if vid.score is None:
            # calculate sentiment score if neccesary
            vid.calculate_sentiment()
            needs_update = True
        # add to database or replace existing entry if changes have
        # been made
        if db_entry is None:
            vid.add_to_db()
        elif needs_update:
            db.session.delete(db_entry)
            vid.add_to_db()
            db.session.commit()
        # set meta attributes for the corresponding Redis Queue task
        _add_video(vid)
        i += 1
        _set_progress(i, max_results)


def _set_progress(num, max):
    """Updates the 'current' and 'total' meta attribute of the current Redis
        Queue task.

        Args:
            num: the number of videos that have been downloaded and scored.
            max: the number of total videos.
    """
    job = get_current_job()
    progress = num/max
    job.meta['current'] = num
    job.meta['total'] = max
    if num == max:
        _report_done()
    job.save_meta()


def _add_video(video):
    """Updates the 'videos' meta attribute of the current Redis Queue task.

        Args:
            video: A serialized depiction of a Youtube_Video object which has
            been finished processing.
    """
    job = get_current_job()
    if 'videos' in job.meta.keys():
        job.meta['videos'].append(video)
    else:
        job.meta['videos'] = [video]
    job.save_meta()


def _report_done():
    """
    """
    job = get_current_job()
    job.meta['complete'] = True
    job.complete = True
    job.save_meta()
