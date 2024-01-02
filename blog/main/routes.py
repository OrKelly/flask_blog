from flask import Blueprint, render_template, request, url_for, redirect
from flask_login import login_required, current_user

from blog.models import Post, User

main = Blueprint('main', __name__, template_folder='templates')


@main.route('/')
def index():
    return render_template('main/index.html', title='Главная')


@main.route('/blog', methods=['POST', 'GET'])
@login_required
def blog():
    all_posts = Post.query.order_by(Post.title.desc()).all()
    all_users = User.query.all()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_post.desc()).paginate(page=page, per_page=4)

    return render_template('main/blog.html', title='Блог', posts=posts,
                           all_posts=all_posts, all_users=all_users)


@main.route('/top')
@login_required
def top():
    all_posts = Post.query.order_by(Post.views.desc()).limit(10).all()
    all_users = User.query.all()
    admins = User.query.filter_by(role='admin').all()
    return render_template('main/top.html', admins=admins, posts=all_posts, all_users=all_users)






