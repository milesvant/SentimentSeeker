import httplib2
import os
import re
import sys
import yaml
from apiclient.discovery import build_from_document
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets

CLIENT_SECRETS_FILE = "%s/yt_config/client_secrets.json" % os.path.abspath(
    os.path.dirname(__file__))
CONFIG_FILE = "%s/yt_config/youtube_config.yaml" % os.path.abspath(os.path.dirname(__file__))

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the {{ Cloud Console }}
{{ https://cloud.google.com/console }}

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))


# Authorize the request and store authorization credentials.
def get_authenticated_service(args):
    with open(CONFIG_FILE) as y:
        config_data = yaml.safe_load(y)
        flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                                       scope=config_data['YOUTUBE_READ_WRITE_SSL_SCOPE'],
                                       message='MISSING_CLIENT_SECRETS_MESSAGE')

    storage = Storage("yt_config/%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        flags = argparser.parse_args('--auth_host_name localhost --logging_level INFO'.split())
        credentials = run_flow(flow, storage, flags)

    # Trusted testers can download this discovery document from the developers page
    # and it should be in the same directory with the code.
    with open("yt_config/youtube-v3-api-captions.json", "r") as f:
        doc = f.read()
        return build_from_document(doc, http=credentials.authorize(httplib2.Http()))


def process_caption(caption):
    caption = re.sub("(\\n|)(\\n|)[0-9]+\\n(([0-9]|:|,| --> ))+\\n", " ", caption)
    caption = re.sub("( |)\[([a-z]|[A-Z])+\]", ".", caption)  # or just space?
    caption = re.sub("\n", "", caption)
    return caption


def get_caption(args, videoid=None, language="en"):
    youtube = get_authenticated_service(args)

    if videoid == None:
        results = youtube.captions().list(
            part="snippet",
            videoId=args.videoid
        ).execute()
    else:
        # try:
        results = youtube.captions().list(
            part="snippet",
            videoId=videoid
        ).execute()
        # TODO try-except block

    # Finds first caption in the requested language
    for item in results["items"]:
        if item["snippet"]["language"] == language:
            subtitle = youtube.captions().download(
                id=item["id"],
                tfmt='srt',
            ).execute()
            # return subtitle.decode("utf-8")
            return process_caption(subtitle.decode("utf-8"))
    # Returns None if there are no captions in the requested language
    return None
