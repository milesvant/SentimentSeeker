from flask import render_template, flash, redirect, url_for, request
from flask import current_app, jsonify
from flask_login import current_user, login_required
from datetime import datetime
from app import db
from app.main import bp
from app.main.forms import EditProfileForm, PostForm
from app.main.forms import YoutubeSearchForm, TwitterSearchForm
from app.main.youtube.sort_videos import sort_videos
from app.main.twitter.sort_tweets import sort_tweets
from app.models import User, Post, YoutubeVideoDB, TweetDB
from app.ml.ml_task import run_update_sentiment
import redis


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


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


@bp.route('/licenses', methods=['GET'])
def licenses():
    return render_template('about/licenses.html')


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
        if (len(YoutubeVideoDB.query.filter_by(correct=True).all()) +
                len(YoutubeVideoDB.query.filter_by(correct=False).all())) % 10 == 0:
            current_app.task_queue.enqueue(run_update_sentiment)
    return jsonify()


@bp.route('/incorrect_video/<videoid>', methods=['POST'])
def incorrect_video(videoid):
    video = YoutubeVideoDB.query.filter_by(videoid=videoid).first()
    if video is not None:
        video.correct = False
        db.session.commit()
        if (len(YoutubeVideoDB.query.filter_by(correct=True).all()) +
                len(YoutubeVideoDB.query.filter_by(correct=False).all())) % 10 == 0:
            current_app.task_queue.enqueue(run_update_sentiment)
    return jsonify()


@bp.route('/correct_tweet/<twitter_id>', methods=['POST'])
def correct_tweet(twitter_id):
    tweet = TweetDB.query.filter_by(twitter_id=str(twitter_id)).first()
    if tweet is not None:
        tweet.correct = True
        db.session.commit()
        if (len(TweetDB.query.filter_by(correct=True).all()) +
                len(TweetDB.query.filter_by(correct=False).all())) % 10 == 0:
            current_app.task_queue.enqueue(run_update_sentiment)
    return jsonify()


@bp.route('/incorrect_tweet/<twitter_id>', methods=['POST'])
def incorrect_tweet(twitter_id):
    tweet = TweetDB.query.filter_by(twitter_id=str(twitter_id)).first()
    if tweet is not None:
        tweet.correct = False
        db.session.commit()
        if (len(TweetDB.query.filter_by(correct=True).all()) +
                len(TweetDB.query.filter_by(correct=False).all())) % 10 == 0:
            current_app.task_queue.enqueue(run_update_sentiment)
    return jsonify()


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username,
                       page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user', username=user.username,
                       page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('main.user', username=username))


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("index.html", title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)
