from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, request
from utils.utils import Role
from extensions import db
from modules.users.models import User


class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == Role.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))

class SecureAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == Role.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))

def setup_admin(app):
    admin = Admin(
        app,
        name='Database Manager',
        url='/db-admin',
        index_view=SecureAdminIndexView(endpoint='db_admin', url='/db-admin')
    )

    admin.add_view(SecureModelView(User, db.session, name="Quản lý Người Dùng", endpoint="admin_user"))