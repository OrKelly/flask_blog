import os
import secrets

from flask import current_app
from flask_login import current_user
from PIL import Image

def save_picture(form_picture):
    random_hex = secrets.token_hex(16)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    full_path = os.path.join(current_app.root_path, 'static', 'profile_pics',
                             current_user.username, 'account_image')
    if not os.path.exists(full_path):
        os.mkdir(full_path)

    picture_path = os.path.join(full_path, picture_fn)
    output_size = (360, 360)

    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

def save_picture_post(form_picture):
    random_hex = secrets.token_hex(16)
    _,f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex+f_ext
    full_path = os.path.join(current_app.root_path, 'static', 'profile_pics',
                            current_user.username, 'post_images')
    if not os.path.exists(full_path):
        os.mkdir(full_path)

    picture_path = os.path.join(full_path,picture_fn)
    output_size = (500,500)

    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn
