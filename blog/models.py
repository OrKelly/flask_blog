from datetime import datetime

from flask import current_app
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer

from blog import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    role = db.Column(db.String(20), index=True, default='Пользователь')
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(), nullable=False, default='default.jpg')
    password = db.Column(db.String(), nullable=False)
    last_seen = db.Column(db.DateTime)
    posts = db.relationship('Post',backref='author',lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'User({self.id}, {self.username}, {self.email}, {self.password}, {self.image_file})'


class Post(db.Model):
    __tablename__ = 'posts'
    __searchable__ = ['title', 'content']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_post = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text(60), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(), unique=True, index=True)

    image_post = db.Column(db.String(30), nullable=True, default='default.jpg')

    views = db.Column(db.Integer, default=0)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comments = db.relationship('Comment', backref='comment_post', lazy=True, cascade="all, delete-orphan")
    tags = db.relationship('Tag', backref='tag_post', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'User({self.title}, {self.date_post}, {self.image_post})'

class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    body = db.Column(db.Text(200), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    image_file = db.Column(db.String(30), nullable=True, default='default.jpg')
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f'Comment({self.body}, {self.date_posted.strftime("%d.%m.%Y-%H.%M")}, {self.post_id})'

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f'Tag({self.id}, {self.name}, {self.post_id})'

class Logs(db.Model):
    __tablename__ = 'logs'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(60))
    username = db.Column(db.String(60))
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f'Log({self.id}, {self.username}, {self.type})'