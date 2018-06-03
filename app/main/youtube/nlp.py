from textblob import TextBlob


def get_sentiment(str):
    if str is None:
        return 0
    else:
        tb = TextBlob(str)
        return (tb.sentiment.polarity * tb.sentiment.subjectivity)


def sentiment_list(caps):
    score_dict_pos = {}
    score_dict_neg = {}
    for cap in caps.keys():
        score = get_sentiment(caps[cap])
        if(score >= 0):
            score_dict_pos[cap] = get_sentiment(caps[cap])
        else:
            score_dict_neg[cap] = get_sentiment(caps[cap])
    sorted_list_pos = sorted(score_dict_pos, key=lambda k: score_dict_pos[k])
    sorted_list_neg = sorted(score_dict_neg, key=lambda k: score_dict_neg[k])
    return_dict = {}
    return_dict['pos'] = sorted_list_pos
    return_dict['neg'] = sorted_list_neg
    return return_dict
