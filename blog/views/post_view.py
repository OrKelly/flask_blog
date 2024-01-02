import os

from flask import url_for, redirect
from flask_login import current_user
from markupsafe import Markup
from flask_admin import form
from flask_admin.contrib.sqla import ModelView

from blog.models import Post, User


file_path = os.path.abspath(os.path.dirname(__name__))


def name_gen_image(model, file_data):
    hash_name = f'{model.author}/post_id-{model.id}/{file_data.filename}'
    return hash_name


class PostView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def _handle_view(self, name, *args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('users.login', next="/admin"))
        if not self.is_accessible:
            return self.render("users.login")

    column_labels = {
        'id': 'ID',
        'author.username': 'Автор',
        'tag_post': 'Тег поста',
        'title': 'Заголовок',
        'image_post': 'Изображение поста',
        'category': 'Категория',
        'slug': 'Слаг',
        'text': 'Текст',
        'date_post': 'Дата',
        'user': 'Пользователь',
        'username': 'Имя',
        'tag': 'Тег',
        'tags': 'Теги',
        'name': 'Имя',
    }

    can_create = False
    can_edit = True
    can_delete = True

    column_list = ['id', 'author.username', Post.title, 'image_post', 'tags']
    column_default_sort = ('title', True)
    column_sortable_list = ('id', 'author', 'title', 'tags')
    column_exclude_list = []
    column_searchable_list = ['title']
    column_filters = ['title', User.username, 'tags']
    column_editable_list = ['title']

    create_modal = True
    edit_modal = True

    form_widget_args = {
        'text': {
            'rows': 5,
            'class': 'w-100 border border-info text-success'
        },

    }

    def _list_thumbnail(view, context, model, name):
        if not model.image_post:
            return ''

        url = url_for('static',
                      filename=os.path.join('profile_pics/' + model.author.username + '/post_images/' + model.image_post))
        if model.image_post.split('.')[-1] in ['jpg', 'jpeg', 'png', 'svg', 'gif']:
            return Markup(f'<img src={url} width="100">')

    # передаю функцию _list_thumbnail в поле image_user
    column_formatters = {
        'image_post': _list_thumbnail
    }


    form_excluded_columns = ['id','date_post', 'author']


    def create_form(self, obj=None):
         return super(PostView, self).create_form(obj)

    def edit_form(self, obj=None):
        return super(PostView, self).edit_form(obj)
