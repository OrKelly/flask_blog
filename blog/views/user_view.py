import os

from flask import url_for, redirect
from flask_admin import form
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from markupsafe import Markup
from wtforms import validators
from blog.models import User
from blog import bcrypt



file_path = os.path.abspath(os.path.dirname(__name__))
def name_gen_image(model, file_data):
    hash_name = f'{model}/{model.username}'
    return hash_name

def gen_basepath(model):
    path = os.path.join(file_path, 'profile_pics/' + model.username +'/account_image/')
    return path

def gen_relativepath(model):
    path = 'profile_pics/'+model.username+'/account_image/'
    return path
class UserView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def _handle_view(self, name, *args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('users.login', next="/admin"))
        if not self.is_accessible:
            return self.render("users.login")

    column_display_pk = True
    column_labels = {
        'id': 'ID',
        'username': 'Имя пользователя',
        'last_seen': 'Последний вход',
        'image_file': 'Аватар',
        'posts': 'Посты',
        'email': 'Емайл',
        'password': 'Пароль',
        'role': 'Роль',
        'file': 'Выберите изображение'
    }

    column_list = ['id','username','role','email','last_seen', 'image_file']

    column_default_sort = ('id', True)
    column_sortable_list = ('id','username','role','email','last_seen')

    can_edit = True
    can_create = False
    can_delete = True
    can_export = True
    export_max_rows = 500
    export_types = ['csv']

    form_args = {
        'username': dict(label='Пользователь', validators=[validators.DataRequired()]),
        'email': dict(label='Почта', validators=[validators.Email()]),
    }

    AVAILABLE_USER_TYPES = [
        (u'admin', u'admin'),
        (u'Пользователь', u'Пользователь'),
    ]

    form_choices = { 'role': AVAILABLE_USER_TYPES, }

    column_descriptions = dict(
        username='Имя пользователя',
        last_seen='Дата последнего входа пользователя'
    )

    column_exclude_list = ['password']

    column_searchable_list = ['email', 'username']
    column_filters = ['email', 'username', 'role']
    column_editable_list = ['role', 'username', 'email']

    create_modal = True
    edit_modal = True

    form_excluded_columns = ['id', 'last_seen']

    def _list_thumbnail(view, context, model, name):
        if not model.image_file:
            return ''

        url = url_for('static', filename=os.path.join('profile_pics/' + model.username +'/account_image/'+ model.image_file))
        if model.image_file.split('.')[-1] in ['jpg', 'jpeg', 'png', 'svg', 'gif']:
            return Markup(f'<img src={url} width="100">')

    column_formatters = {
        'image_file': _list_thumbnail
    }

    # form_extra_fields = {
    #     # ImageUploadField Выполняет проверку изображений, создание эскизов, обновление и удаление изображений.
    #     "image_file": form.ImageUploadField('',
    #                                         # Абсолютный путь к каталогу, в котором будут храниться файлы
    #                                         base_path=
    #                                         os.path.join(file_path, 'blog/static/storage/user_img/'),
    #                                         # Относительный путь из каталога. Будет добавляться к имени загружаемого файла.
    #                                         url_relative_path='storage/user_img/',
    #                                         namegen=name_gen_image,
    #                                         # Список разрешенных расширений. Если не указано, то будут разрешены форматы gif, jpg, jpeg, png и tiff.
    #                                         allowed_extensions=['jpg'],
    #                                         max_size=(1200, 780, True),
    #                                         thumbnail_size=(100, 100, True),
    #
    #                                         )}


    def create_form(self, obj=None):
        return super(UserView, self).create_form(obj)

    def edit_form(self, obj=None):
        return super(UserView, self).edit_form(obj)

    def on_model_change(self, view, model, is_created):
        model.password = bcrypt.generate_password_hash(model.password)