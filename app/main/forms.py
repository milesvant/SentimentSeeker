from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField


class YoutubeSearchForm(FlaskForm):
    queryyt = TextAreaField('Search Youtube')
    submityt = SubmitField('Submit')


class TwitterSearchForm(FlaskForm):
    querytwt = TextAreaField('Search Twitter')
    submittwt = SubmitField('Submit')
