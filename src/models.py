from flask_sqlalchemy import SQLAlchemy
import datetime
from datetime import datetime, timezone

db = SQLAlchemy()

# Association table for subscriptions
subscriptions = db.Table('subscriptions',
    db.Column('subscriber_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('subscribed_to_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    avatar = db.Column(db.String(255), nullable=True)
    videos = db.relationship('Video', backref='author', lazy=True)
    # Relationships for subscribers and subscriptions
    subscribed_to = db.relationship('User', secondary='subscriptions',
                                  primaryjoin=(subscriptions.c.subscriber_id == id),
                                  secondaryjoin=(subscriptions.c.subscribed_to_id == id),
                                  backref=db.backref('subscribers', lazy='dynamic'),
                                  lazy='dynamic')

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text(500), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)
    comments = db.relationship('Comment', lazy=True)  # Removed backref
    views = db.Column(db.Integer, default=0)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)

class DisLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    user = db.relationship('User', backref='comments') 

    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    video = db.relationship('Video') 