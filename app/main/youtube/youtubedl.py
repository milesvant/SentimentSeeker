import os
import re


def vtt_to_plaintext(caption):
    caption = re.sub("(\\n|)(\\n|)[0-9]+\\n(([0-9]|:|,| --> ))+\\n", " ", caption)
    caption = re.sub("( |)\[([a-z]|[A-Z])+\]", "", caption)
    caption = re.sub("\n", "", caption)
    return caption


def ttml_to_plaintext(caption):
    caption = re.sub("<([^>])+>", "", caption)
    caption = re.sub("&#39;", "\'", caption)
    caption = re.sub("( |)\[([a-z]|[A-Z])+\]", "", caption)
    caption = re.sub("\n", " ", caption)
    return caption


def download_sub(videoid):
    # TODO: time/file-size limit on captions?
    conf_location = "%s/yt_config/youtube-dl.conf" % os.path.abspath(os.path.dirname(__file__))
    os.system(
        "youtube-dl --config-location %s -o %s https://www.youtube.com/watch?v=%s" % (
            conf_location, videoid, videoid))
    caption = open("%s.en.ttml" % videoid).read()
    os.system("rm %s.en.ttml" % videoid)
    return ttml_to_plaintext(caption)
