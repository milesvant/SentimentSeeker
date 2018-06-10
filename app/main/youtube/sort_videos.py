from app import db, celery
from app.models import YoutubeVideoDB
from app.main.youtube.search import youtube_search
from app.main.youtube.youtube_video import Youtube_Video


@celery.task(bind=True)
def sort_videos(self, query, max_results=10):
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
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': max_results})
        i += 1
    pos_videos = list(filter(lambda x: x.score > 0, videos))
    neg_videos = list(filter(lambda x: x.score <= 0, videos))
    pos_videos.sort(key=lambda x: x.score)
    neg_videos.sort(key=lambda x: x.score, reverse=True)
    return pos_videos, neg_videos
