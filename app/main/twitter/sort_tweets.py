import os
import sys
from app import db
from app.models import TweetDB
from app.main.twitter.search_twitter import search_twitter
from app.main.twitter.tweet import Tweet
from topic import create_app


def sort_tweets(query, max_request=20):
    """Takes a query and searches Twitter's API for a list of tweets matching
        that query, then calculates their sentiment scores.

        Args:
            query: A string query.
            max_request: The maximum number of results requested, default is
                10.
        Returns:
            A list of positively categorized tweets, followed by a list of
                negatively categorized tweets
    """
    tweets = search_twitter(query, max_request)
    max_results = len(tweets)
    for twt in tweets:
        # Search for matching entry in database
        db_entry = twt.find_db_entry()
        needs_update = False
        if db_entry is not None:
            # replace tweet with db entry if one exists
            twt.from_db_entry(db_entry)
        if twt.score is None:
            # calculate sentiment score if neccesary
            twt.calculate_sentiment()
            needs_update = True
        # add to database or replace existing entry if changes have
        # been made
        if db_entry is None:
            # twt.add_to_db()
        elif needs_update:
            db.session.delete(db_entry)
            # twt.add_to_db()
            db.session.commit()
    positive_tweets = list(filter(lambda x: x.score > 0, tweets))
    negative_tweets = list(filter(lambda x: x.score <= 0, tweets))
    return positive_tweets, negative_tweets
