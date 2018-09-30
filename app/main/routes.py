from flask import render_template, flash, redirect, url_for, request
from flask import current_app, jsonify
from datetime import datetime
from app import db
from app.main import bp
from app.main.forms import YoutubeSearchForm, TwitterSearchForm
from app.main.youtube.sort_videos import sort_videos
from app.main.twitter.sort_tweets import sort_tweets
from app.models import YoutubeVideoDB, TweetDB
import redis


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    ytform = YoutubeSearchForm()
    twtform = TwitterSearchForm()
    if ytform.queryyt.data and ytform.validate_on_submit():
        q = ytform.queryyt.data
        return redirect(url_for('main.video_results', query=q))
    if twtform.querytwt.data and twtform.validate_on_submit():
        q = twtform.querytwt.data
        return redirect(url_for('main.twitter_results', query=q))
    return render_template('index.html',
                           title='Home',
                           ytform=ytform,
                           twtform=twtform)


@bp.route('/about', methods=['GET'])
def about():
    return render_template('about/about.html')


@bp.route('/video_results/<query>', methods=['GET', 'POST'])
def video_results(query):
    form = YoutubeSearchForm()
    if form.validate_on_submit():
        q = form.queryyt.data
        return redirect(url_for('main.video_results', query=q))
    return render_template('youtube/results.html', form=form, query=query)


@bp.route('/download_video/<query>', methods=['POST'])
def download_video(query):
    task = current_app.task_queue.enqueue(sort_videos, args=[query])
    task.meta['progress'] = 0
    return jsonify({}), 202, {'Location':
                              url_for('main.download_video_status',
                                      task_id=task.get_id())}


@bp.route('/download_video_status/<task_id>')
def download_video_status(task_id):
    """
    """
    task = current_app.task_queue.fetch_job(task_id)
    response = {}
    if task is None or task.is_failed:
        response = {'state': 'FAILED'}
    else:
        progress = 0
        state = 'PROGRESS'
        if 'current' in task.meta.keys():
            response = {
                'state': state,
                'current': task.meta['current'],
                'total': task.meta['total'],
                'status': 'running',
            }
        if 'videos' in task.meta.keys():
            # adds a list of the to-be-displayed videos to the JSON response
            video_list = []
            for video in task.meta['videos']:
                video_list.append(video.serialize())
            response['videos'] = video_list
        if 'complete' in task.meta.keys():
            response['state'] = 'DONE'
    return jsonify(response)


@bp.route('/twitter_results/<query>', methods=['GET', 'POST'])
def twitter_results(query):
    form = TwitterSearchForm()
    if form.validate_on_submit():
        q = form.querytwt.data
        return redirect(url_for('main.twitter_results', query=q))
    positive_tweets, negative_tweets = sort_tweets(query)
    return render_template('twitter/results.html',
                           form=form,
                           positive_tweets=positive_tweets,
                           negative_tweets=negative_tweets)


@bp.route('/correct_video/<videoid>', methods=['POST'])
def correct_video(videoid):
    video = YoutubeVideoDB.query.filter_by(videoid=videoid).first()
    if video is not None:
        video.correct = True
        db.session.commit()
    return jsonify()


@bp.route('/incorrect_video/<videoid>', methods=['POST'])
def incorrect_video(videoid):
    video = YoutubeVideoDB.query.filter_by(videoid=videoid).first()
    if video is not None:
        video.correct = False
        db.session.commit()
    return jsonify()


@bp.route('/correct_tweet/<twitter_id>', methods=['POST'])
def correct_tweet(twitter_id):
    tweet = TweetDB.query.filter_by(twitter_id=str(twitter_id)).first()
    if tweet is not None:
        tweet.correct = True
        db.session.commit()
    return jsonify()


@bp.route('/incorrect_tweet/<twitter_id>', methods=['POST'])
def incorrect_tweet(twitter_id):
    tweet = TweetDB.query.filter_by(twitter_id=str(twitter_id)).first()
    if tweet is not None:
        tweet.correct = False
        db.session.commit()
    return jsonify()
