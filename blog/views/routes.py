from flask import url_for, redirect, request
from flask_admin import expose, BaseView, AdminIndexView
from flask_login import login_required, current_user
from sqlalchemy import desc

from blog.models import Logs


class DashBoardView(AdminIndexView):
    @login_required
    @expose('/')
    def admin_panel(self):
        if current_user.is_admin:
            from blog.models import User
            page = request.args.get('page', 1, type=int)
            logs = Logs.query.order_by(Logs.date.desc()).paginate(page=page, per_page=5)
            all_users = User.query.all()
            image_file = url_for('static',
                                 filename=f'profile_pics/' + current_user.username + '/account_image/' +
                                          current_user.image_file)
            return self.render('admin/index_admin.html', all_users=all_users, image_file=image_file, logs=logs)
        else:
            return redirect(url_for('users.login'))



class AnyPageView(BaseView):
    @expose('/')
    def any_page(self):

        return self.render('main/index.html')
