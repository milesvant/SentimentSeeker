import twitter
import yaml
import os

CONFIG_FILE = "{}/twitter_config.yaml".format(
    os.path.abspath(os.path.dirname(__file__)))


def twitter_search(query, max_results=10):
    # load config data from twitter_config.yaml
    with open(CONFIG_FILE) as y:
        c = yaml.safe_load(y)
        twitter_api = twitter.api(consumer_key=c['CONSUMER_KEY'],
                                  consumer_secret=c['CONSUMER_SECRET'],
                                  access_token_key=c['ACCESS_TOKEN'],
                                  access_token_secret=c['ACCESS_TOKEN_SECRET'])
