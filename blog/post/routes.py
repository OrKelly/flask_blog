import os

from flask import Blueprint, flash, redirect, url_for, render_template, abort, request, current_app
from flask_login import current_user, login_required
from slugify import slugify

from blog import db
from blog.models import Post, Comment, Tag, Logs
from blog.post.forms import PostForm, PostUpdateForm, CommentUpdateForm
from blog.post.utils import save_picture_post
from blog.user.forms import AddCommentForm

posts = Blueprint('posts', __name__, template_folder='templates')


@posts.route('/post/new', methods=['GET','POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, category=form.category.data,
                    image_post=form.picture.data, author=current_user)
        picture_file = save_picture_post(form.picture.data)
        post.image_post = picture_file
        db.session.add(post)
        post.slug = slugify(post.title)
        db.session.flush()

        name = form.tag_form.data.split('/')
        for i in name:
            tag_post = Tag(name=i)
            tag_post.post_id = post.id
            db.session.add(tag_post)
        log = Logs(type=f'Пользователь {current_user.username} создал пост с названием {post.title} в тематике {post.category}')
        db.session.add(log)
        db.session.commit()
        flash('Пост был опубликован!', 'success')
        return redirect(url_for('main.blog'))

    image_file = url_for('static', filename=f'profile_pics/'+
                            current_user.username+'/post_images/'+ current_user.image_file)

    return render_template('post/create_post.html', title='Новая статья', form=form,
                           legend='Новая статья', image_file=image_file)

@posts.route('/post/<string:slug>', methods=['GET', 'POST'])
@login_required
def post(slug):
    post = Post.query.filter_by(slug=slug).first()
    comment = Comment.query.filter_by(post_id=post.id).order_by(db.desc(Comment.date_posted)).all()
    post.views += 1

    form_post = PostForm()
    form_comment = AddCommentForm()
    if request.method == 'POST':
        def add_tag():
            name = form_post.tag_form.data
            if name:
                name = name.split('/')
                for i in name:
                    tag_post = Tag(name=i)  # создаю тег
                    tag_post.post_id = post.id
                    db.session.add(tag_post)
                db.session.commit()
                flash('Тег к посту был добавлен', "success")
                return redirect(url_for('posts.post', slug=post.slug))

        add_tag()

    if request.method == 'POST' and form_comment.validate_on_submit():
        username = current_user.username
        image_file = current_user.image_file
        comment = Comment(username=username, body=form_comment.body.data, post_id=post.id, image_file=image_file)
        db.session.add(comment)
        log = Logs(type=f'Пользователь {current_user.username} добавил комментарий к посту {post.title}')
        db.session.add(log)
        db.session.commit()
        flash('Комментарий к посту был добавлен', "success")
        return redirect(url_for('posts.post', slug=post.slug))
    form_post.tag_form.data = ''
    image_file = url_for('static',
                         filename=f'profile_pics/'+ post.author.username + '/post_images/' + post.image_post)
    return render_template('post/post.html', title=post.title, post=post, image_file=image_file,
                           form_add_comment=form_comment, comment=comment, form_add_tag=form_post)
@posts.route('/search')
def search():
    keyword = request.args.get('q')
    search_posts = Post.query.whoosh_search(keyword)
    return render_template('post/search.html', search_posts=search_posts)


@posts.route('/post/<string:slug>/update', methods=['GET', 'POST'])
@login_required
def update_post(slug):
    post = Post.query.filter_by(slug=slug).first()

    if post.author != current_user or not current_user.is_admin:
        flash('Нет доступа к обновлению статьи!', 'danger')
        return redirect(url_for('posts.post', slug=post.slug))

    form = PostUpdateForm()
    if request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.category.data = post.category

    if form.validate_on_submit():
        post_title_old = post.title
        post.title = form.title.data
        post.content = form.content.data
        post.category = form.category.data
        if form.picture.data:
            post.image_post = save_picture_post(form.picture.data)
        log = Logs(type=f'Пользователь {current_user.username} изменил пост {post_title_old}')
        db.session.add(log)
        db.session.commit()
        flash('Данный пост был обновлён', 'success')

        return redirect(url_for('posts.post', slug=slug))

    image_file = url_for('static',
                         filename=f'profile_pics/{current_user.username}/post_images/{post.image_post}')

    return render_template('post/update_post.html', title='Обновить статью',
                           form=form, legend='Обновить статью', image_file=image_file, post=post)


@posts.route('/post/<string:slug>/delete', methods=['POST'])
@login_required
def delete_post(slug):
    post = Post.query.filter_by(slug=slug).first()
    admin = current_user.is_admin
    if admin == False and post.author != current_user:
        flash('Нет доступа к удалению статьи!', 'danger')
        return redirect(url_for('posts.post', slug=post.slug))

    try:
        post_title = post.title
        os.unlink(
            os.path.join(current_app.root_path,
                         f'static/profile_pics/users/{current_user.username}/post_images/{post.image_post}'))
        db.session.delete(post)
    except:
        db.session.delete(post)
    log = Logs(type=f'Пользователь {current_user.username} удалил пост {post_title}')
    db.session.add(log)

    db.session.commit()
    flash('Данный пост был удален', 'success')
    return redirect(url_for('users.account'))

@posts.route('/comment/<int:comment_id>/update/', methods=['GET', 'POST'])
@login_required
def update_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.username != current_user.username or not current_user.is_admin:
        flash('Нет доступа к обновлению комментария!', 'danger')
        return redirect(url_for('posts.post', slug=post.slug))

    form = CommentUpdateForm()
    if request.method == 'GET':
        form.body.data = comment.body
    if form.validate_on_submit():
        comment.body = form.body.data
        log = Logs(type=f'Пользователь {current_user.username} обновил комментарий с айди {comment.id} к посту {comment.comment_post.title}')
        db.session.add(log)
        db.session.commit()
        return redirect(url_for('posts.post', slug=comment.comment_post.slug))
    return render_template('post/update_comment.html', form=form, title='Обновить комментарий')

@posts.route('/post/comment/<int:comment_id>/delete')
@login_required
def delete_comment(comment_id):
    single_comment = Comment.query.get_or_404(comment_id)
    return_to_post = single_comment.comment_post.slug

    if current_user.is_admin or single_comment.username == current_user.username:
        log = Logs(type=f'Пользователь {current_user.username} удалил комментарий с айди {single_comment.id} к посту {single_comment.comment_post.title}')
        db.session.add(log)
        db.session.delete(single_comment)
        db.session.commit()
        flash('Комментарий был удалён', 'success')
    else:
        abort(403)
    return redirect(url_for('posts.post', slug=return_to_post))

@posts.route('/posts/<string:category>', methods=['GET', 'POST'])
@login_required
def category(category):
    current_category = Post.query.filter_by(category=category).first()
    posts_category = Post.query.filter_by(category=category).all()
    return render_template('post/all_posts_category.html', post_category=posts_category,
                           current_category=current_category, title='Рубрика ' + category)


@posts.route('/tags/<string:tag_str>', methods=['GET', 'POST'])
@login_required
def tag(tag_str):
    current_tag = Tag.query.filter_by(name=tag_str).first_or_404()
    name_tags = Tag.query.filter(Tag.name == current_tag.name).all()
    return render_template('post/all_post_tag.html', name_tags=name_tags,
                           current_tag=current_tag, title='Статьи тега ' + current_tag.name)

@posts.route('/post/tag/<int:tag_id>/delete', methods=['POST', 'GET'])
@login_required
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    if tag.tag_post.author != current_user:
        abort(403)
    db.session.delete(tag)
    db.session.commit()
    flash('Тег удален', 'success')
    return redirect(url_for('posts.post', slug=tag.tag_post.slug))
