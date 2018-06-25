import yaml
import os
from app.main.youtube.youtube_video import Youtube_Video
from googleapiclient.discovery import build


def youtube_search(query, max_results=10):
    CONFIG_FILE = "{}/youtube_config.yaml".format(
        os.path.abspath(os.path.dirname(__file__)))
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as y:
            config_data = yaml.load(y)
            asn = config_data['YOUTUBE_API_SERVICE_NAME']
            av = config_data['YOUTUBE_API_VERSION']
            devkey = config_data['DEVELOPER_KEY']
    else:
        asn = os.environ.get('YOUTUBE_API_SERVICE_NAME')
        av = os.environ.get('YOUTUBE_API_VERSION')
        devkey = os.environ.get('YOUTUBE_DEVELOPER_KEY')
    youtube = build(asn, av, developerKey=devkey)

    # Call the search().list method to retrieve results matching the specified
    # query term.
    search_response = youtube.search().list(
        q=query,
        type="video",
        part="id,snippet",
        maxResults=max_results,
        videoCaption="closedCaption",
    ).execute()

    # Convert each video response into a Youtube_Video object and add it to the
    # list that will be returned.
    videos = []
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            yv = Youtube_Video(search_result["id"]["videoId"],
                               search_result["snippet"]["title"])
            videos.append(yv)
    return videos
