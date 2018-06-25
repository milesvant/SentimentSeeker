from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from datetime import datetime
from app import db, login
from time import time
import jwt


class LogisticRegressionModel(db.Model):
    """Database model for storing trained Logistic Regression models, along
        with their respective accuracies."""
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.LargeBinary, unique=False)
    accuracy = db.Column(db.Float, unique=False)
    vectorizer = db.Column(db.LargeBinary, unique=False)
    use_me = db.Column(db.Boolean)

    def __cmp__(self, other):
        """Comparisons betwen LogisticRegressionModel are done by comparing
            their respective accuracies."""
        return __cmp__(self.accuracy, other.accuracy)


class InitialTrainingDataDB(db.Model):
    """Database model for the initial (online movie review) data used to train
       the sentiment classifier."""
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(10000), unique=False)
    positive = db.Column(db.Boolean)


class YoutubeVideoDB(db.Model):
    """Database model for a Youtube Video"""
    id = db.Column(db.Integer, primary_key=True)
    videoid = db.Column(db.String(12), index=True, unique=True)
    title = db.Column(db.String(70), index=True, unique=False)
    caption = db.Column(db.String(10000), unique=False, default=None)
    score = db.Column(db.Integer, unique=False, default=None)
    correct = db.Column(db.Boolean, default=None)

    def __repr__(self):
        return '<Youtube Video id:{} title:{} score:{}>'.format(
            self.videoid, self.title, self.score)


class TweetDB(db.Model):
    """Database model for a Tweet"""
    id = db.Column(db.Integer, primary_key=True)
    twitter_id = db.Column(db.String(25), unique=True, index=True)
    name = db.Column(db.String(12), index=True, unique=False)
    text = db.Column(db.String(280), unique=False)
    score = db.Column(db.Integer, unique=False, default=None)
    correct = db.Column(db.Boolean, default=None)

    def __repr__(self):
        return '<Tweet tweeter:{} content:{} score:{}>'.format(
            self.tweeter, self.content. self.score)


followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)
