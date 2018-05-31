from search import youtube_search
from get_captions import get_caption
from nlp import sentiment_list


def search_sort(query):
    args = argparser.parse_args()
    my_video = youtube_search(query, max_results=20)
    captions = {}
    for vid in my_video:
        try:
            captions[vid] = get_caption(args, vid)
            print("yes")
        except HttpError:
            print("no")
            pass
    print(sentiment_list(captions))
