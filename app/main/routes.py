from flask import render_template, flash, redirect, url_for, request
from flask import current_app, jsonify
from flask_login import current_user, login_required
from datetime import datetime
from app import db
from app.main import bp
from app.main.forms import EditProfileForm, PostForm, YoutubeSearchForm
from app.main.youtube.sort_videos import sort_videos
from app.models import User, Post
import redis
from rq import Queue, Connection, get_current_job, get_failed_queue


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    form = YoutubeSearchForm()
    if form.validate_on_submit():
        q = form.query.data
        return redirect(url_for('main.results', query=q))
    return render_template('index.html', title='Home', form=form)


@bp.route('/results/<query>', methods=['GET', 'POST'])
def results(query):
    form = YoutubeSearchForm()
    if form.validate_on_submit():
        q = form.query.data
        return redirect(url_for('main.results', query=q))
    # pos, neg = sort_videos(query)
    return render_template('youtube/results.html', query=query)


@bp.route('/download/<query>', methods=['POST'])
def download(query):
    task = current_app.task_queue.enqueue(sort_videos, args=[query], result_ttl=500)
    task.meta['progress'] = 0
    return jsonify({}), 202, {'Location':
                              url_for('main.download_status',
                                      task_id=task.get_id())}


@bp.route('/download_status/<task_id>')
def download_status(task_id):
    """
    """
    task = current_app.task_queue.fetch_job(task_id)
    response = {}
    print(task.meta)
    if task is None or task.is_failed:
        response = {'state': 'FAILED'}
    else:
        progress = 0
        state = 'PROGRESS'
        if 'progress' in task.meta.keys():
            progress = task.meta['progress']
            response = {
                'state': state,
                'current': progress * 10,
                'total': 10,
                'status': 'running',
            }
        if 'videos' in task.meta.keys():
            # adds videos that haven't been displayed yet to video_list
            video_list = []
            for video in task.meta['videos']:
                video_list.append(video.serialize())
                task.meta['videos'].remove(video)
                task.save_meta()
            response['videos'] = video_list
        if 'complete' in task.meta.keys():
            print("happened")
            response['state'] = 'DONE'
    return jsonify(response)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) \
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
