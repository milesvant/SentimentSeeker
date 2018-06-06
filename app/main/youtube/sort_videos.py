from app.main.youtube.search import youtube_search
from app.main.youtube.youtube_video import Youtube_Video


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
    videos = youtube_search(query, max_results)
    for vid in videos:
        vid.download_sub()
        vid.calculate_sentiment()
    pos_videos = list(filter(lambda x: x.score > 0, videos))
    neg_videos = list(filter(lambda x: x.score <= 0, videos))
    pos_videos.sort(key=lambda x: x.score)
    neg_videos.sort(key=lambda x: x.score, reverse=True)
    return pos_videos, neg_videos
