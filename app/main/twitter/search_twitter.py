import twitter
import yaml
import os

CONFIG_FILE = "%s/twitter_config.yaml" % os.path.abspath(os.path.dirname(__file__))


def twitter_search(query, max_results=10):
    with open(CONFIG_FILE) as y:
        config_data = yaml.safe_load(y)
        twitter_api = twitter.api(consumer_key=config_data['CONSUMER_KEY'],
                                  consumer_secret=config_data['CONSUMER_SECRET'],
                                  access_token_key=config_data['ACCESS_TOKEN'],
                                  access_token_secret=config_data['ACCESS_TOKEN_SECRET'])
