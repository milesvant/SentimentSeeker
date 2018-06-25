import twitter
import yaml
import os
from app.main.twitter.tweet import Tweet


def search_twitter(query, max_results=20):
    """Searches twitter's search API for a query.

        Args:
            query: a search term (without hashtags for now).
            max_results: the maximum number of results desired.
        Returns:
            A list of Tweet objects which are representations of the results
            from Twitter's API response.
    """
    # load config data from twitter_config.yaml
    CONFIG_FILE = "{}/twitter_config.yaml".format(
        os.path.abspath(os.path.dirname(__file__)))
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as y:
            config = yaml.load(y)
        consumer_key = config['CONSUMER_KEY']
        consumer_secret = config['CONSUMER_SECRET']
        access_token_key = config['ACCESS_TOKEN']
        access_token_secret = config['ACCESS_TOKEN_SECRET']
    else:
        consumer_key = os.environ.get('TWITTER_CONSUMER_KEY')
        consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET')
        access_token_key = os.environ.get('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
    twitter_api = twitter.Api(consumer_key,
                              consumer_secret,
                              access_token_key,
                              access_token_secret)
    # search twitter api for query (sorted by popular)
    results = twitter_api.GetSearch(
        raw_query="q={}&lang=en&result_type=popular&count={}".format(
            query, max_results))
    # convert the result into a list of Tweet objects
    tweet_list = []
    for result in results:
        result_tweet = Tweet(name=result.user.name,
                             text=result.text,
                             id=result.id,)
        tweet_list.append(result_tweet)
    return tweet_list
