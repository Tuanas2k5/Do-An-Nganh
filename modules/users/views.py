from flask import Blueprint, render_template, request, redirect, url_for, flash
from modules.users.services import register_new_user, verify_user_login
from flask_login import login_user, logout_user, login_required

user_bp = Blueprint('user', __name__)


@user_bp.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        form_data = {
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'password': request.form.get('password'),
            'confirm_password': request.form.get('confirm_password')
        }

        success, message = register_new_user(form_data)

        if success:
            flash(message, 'success')
            return redirect(url_for('user.login_page'))
        else:
            flash(message, 'danger')
            return redirect(url_for('user.register_page'))

    return render_template('register.html')


@user_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        success, user = verify_user_login(email, password)
        if success:
            login_user(user, remember=remember)

            flash(f'Chào mừng {user.last_name} đã quay lại!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không chính xác!', 'danger')

    return render_template('login.html')


@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất thành công!', 'info')
    return redirect(url_for('user.login_page'))