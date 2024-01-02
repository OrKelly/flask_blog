import os.path
import shutil
from datetime import datetime

import sqlalchemy.exc
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required

from blog.user.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from blog import bcrypt, db
from blog.models import User, Post, Logs
from blog.user.utils import save_picture, random_avatar, send_reset_email

users = Blueprint('users', __name__, template_folder='templates')

@users.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.blog'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data,password=hashed_password, image_file=random_avatar(form.username.data))
        log = Logs(type=f'Пользователь {form.username.data} зарегистрировался {datetime.now()}')
        db.session.add(user)
        db.session.add(log)
        db.session.commit()

        flash('Ваш аккаунт был успешно создан', 'success')

        return redirect(url_for('users.login'))

    return render_template('users/register.html', form=form, title='Регистрация', legend='Регистрация')

@users.route('/login', methods=['POST','GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.blog'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Вы вошли как пользователь {current_user.username}', 'info')
            return redirect(next_page) if next_page else redirect(url_for('users.account'))
        else:
            flash('Войти не удалось. Пожалуйста, проверьте свой логин и пароль', 'danger')

    return render_template('users/login.html', form=form, title='Авторизация', legend='Войти')

@users.route('/account', methods=['POST','GET'])
@login_required
def account():
    user = User.query.filter_by(username=current_user.username).first()
    posts = Post.query.all()
    users = User.query.all()
    form = UpdateAccountForm()
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    elif form.validate_on_submit():
        path_one = os.path.join(os.getcwd(), f'blog/static/profile_pics/{user.username}')
        path_two = os.path.join(os.getcwd(), f'blog/static/profile_pics/{form.username.data}')
        os.rename(path_one, path_two)
        current_user.username = form.username.data
        current_user.email = form.email.data
        
        if form.picture.data:
            current_user.image_file = save_picture(form.picture.data)
        else:
            form.picture.data = current_user.image_file

        
        db.session.commit()
        flash('Ваш аккаунт был обновлен!', 'success')
        return redirect(url_for('users.account'))

    image_file = url_for('static', filename=f'profile_pics/'+current_user.username
                         +'/account_image/'+ current_user.image_file)
    return render_template('users/account.html', title='Аккаунт', users=users, posts=posts, user=user, image_file=image_file, form=form)

@users.route('/user/<string:username>')
@login_required
def user_posts(username):
    page = request.args.get('page',1,type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user) \
        .order_by(Post.date_post.desc()) \
        .paginate(page=page, per_page=3)

    return render_template('users/user_posts.html', title='Блог', posts=posts, user=user)

@users.route('/user_delete/<string:username>', methods=['GET','POST'])
@login_required
def user_delete(username):
    try:
        user = User.query.filter_by(username=username).first_or_404()
        if user and user.id != 2:
            db.session.delete(user)
            db.session.commit()
            full_path = os.path.join(os.getcwd(),'blog/static','profile_pics', user.username)
            shutil.rmtree(full_path)

            flash(f'Пользователь {username} был удален!', 'info')
            return redirect(url_for('users.account'))

    except sqlalchemy.exc.IntegrityError:
        flash(f'У пользователя {username} есть контент!', 'warning')
        return redirect(url_for('users.account'))
    except FileNotFoundError:
        return redirect(url_for('users.account'))

    else:
        flash('Администрация!', 'info')
        return redirect(url_for('users.account'))

@users.route('/reset_password', methods=['GET','POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('users.account'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash(f'На {form.email.data} были отправлены инструкции по восстановлению пароля', 'info')
        return redirect(url_for('users.login'))
    return render_template('users/reset_request.html', form=form, title='Сброс пароля')

@users.route('/reset_password/<token>', methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('users.account'))
    user = User.verify_user_token(token)
    if user is None:
        flash('Неправильный или просроченный токен!','warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Ваш пароль был обновлен! Вы можете войти на блог!', 'success')
        return redirect(url_for('users.login'))
    return render_template('users/reset_token.html', form=form, title='Сброс пароля')



@users.route('/logout')
@login_required
def logout():
    current_user.last_seen = datetime.now()
    db.session.commit()
    logout_user()
    return redirect(url_for('main.index'))

