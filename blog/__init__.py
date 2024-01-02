from flask import Flask, url_for
from flask_login import LoginManager, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_mail import Mail
from flask_admin import Admin, expose, AdminIndexView, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_babel import Babel


db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()
babel = Babel()

mail = Mail()

login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('settings.py')
    from blog.views.routes import DashBoardView, AnyPageView
    admin = Admin(name='Admin Board', template_mode='bootstrap3', index_view=DashBoardView(), endpoint='admin')

    admin.init_app(app)
    db.init_app(app)
    babel.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    mail.init_app(app)

    from blog.models import User, Post, Comment, Tag
    from blog.views.user_view import UserView
    from blog.views.comment_view import CommentView
    from blog.views.tag_view import TagView
    from blog.views.post_view import PostView

    admin.add_view(UserView(User, db.session, name='Пользователь'))
    admin.add_view(PostView(Post, db.session, name='Статьи'))
    admin.add_view(CommentView(Comment, db.session, name='Комментарии'))
    admin.add_view(TagView(Tag, db.session, name='Теги'))
    admin.add_view(AnyPageView(name='На блог'))

    from blog.main.routes import main
    from blog.user.routes import users
    from blog.post.routes import posts
    from blog.errors.handlers import errors

    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(errors)

    return app


