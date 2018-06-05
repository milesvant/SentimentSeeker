import os
import re
import youtube_dl

DOWNLOADS = "%s/downloads" % os.path.abspath(os.path.dirname(__file__))


def ttml_to_plaintext(caption):
    caption = re.sub("<([^>])+>", "", caption)
    caption = re.sub("&#39;", "\'", caption)
    caption = re.sub("( |)\[([a-z]|[A-Z])+\]", "", caption)
    caption = re.sub("\n", " ", caption)
    return caption


def download_sub(videoid):
    ydl_opts = {
        'skip_download': True,
        'subtitleslangs': 'en',
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'subtitlesformat': 'ttml',
        'outtmpl': '%s/%s' % (DOWNLOADS, videoid),
        'nocheckcertificate': True,
        'quiet': True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(["https://www.youtube.com/watch?v=%s" % videoid])
    caption = open("%s/%s.en.ttml" % (DOWNLOADS, videoid)).read()
    os.system("rm -- %s/%s.en.ttml" % (DOWNLOADS, videoid))
    return ttml_to_plaintext(caption)
