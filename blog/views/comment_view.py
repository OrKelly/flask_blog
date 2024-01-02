from flask import redirect, url_for
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user


class CommentView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def _handle_view(self, name, *args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('users.login', next="/admin"))
        if not self.is_accessible:
            return self.render("users.login")

    column_labels = {
        'name': 'Имя комментария'
    }
    can_delete = True
    can_create = True
    can_edit = True
