import yaml

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.tools import argparser

CONFIG_FILE = "config.yaml"


def youtube_search(query, max_results=25):
    with open(CONFIG_FILE) as y:
        config_data = yaml.safe_load(y)
        youtube = build(config_data['YOUTUBE_API_SERVICE_NAME'],
                        config_data['YOUTUBE_API_VERSION'],
                        developerKey=config_data['DEVELOPER_KEY'])

    # Call the search.list method to retrieve results matching the specified
    # query term.
    search_response = youtube.search().list(
        q=query,
        part="id,snippet",
        maxResults=max_results
    ).execute()

    videos = []

    # Add each result to the appropriate list, and then display the lists of
    # matching videos, channels, and playlists.
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            videos.append("%s" % search_result["id"]["videoId"])
    return videos
