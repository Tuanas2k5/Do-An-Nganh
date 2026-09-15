from flask import Blueprint, render_template, request, redirect, url_for, flash
from modules.users.services import register_new_user, verify_user_login
from modules.exams.models import Submission, ReadingExercise, WritingTopic
from flask_login import login_user, logout_user, login_required, current_user
import cloudinary
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from extensions import db
from modules.users.models import User
from datetime import datetime, timedelta

from utils.utils import Role

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
            return render_template('register.html', form_data=form_data)

    return render_template('register.html', form_data={})


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
            if user.role == Role.ADMIN:
                return redirect(url_for('admin.dashboard'))

            elif user.role == Role.TEACHER:
                return redirect(url_for('teacher.dashboard'))

            else:
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


@user_bp.route('/profile/avatar', methods=['POST'])
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        flash('Không tìm thấy file ảnh!', 'danger')
        return redirect(url_for('user.profile_page'))

    file = request.files['avatar']
    if file.filename == '':
        flash('Bạn chưa chọn ảnh!', 'warning')
        return redirect(url_for('user.profile_page'))

    if file:
        try:
            upload_result = cloudinary.uploader.upload(file)

            secure_url = upload_result.get('secure_url')

            current_user.avatar = secure_url
            db.session.commit()

            flash('Cập nhật ảnh đại diện thành công!', 'success')
        except Exception as e:
            flash(f'Lỗi tải ảnh đám mây: {str(e)}', 'danger')

    return redirect(url_for('user.profile_page'))


@user_bp.route('/profile/avatar/remove', methods=['POST'])
@login_required
def remove_avatar():
    current_user.avatar = 'https://res.cloudinary.com/dwfzctwmt/image/upload/v1787924401/default-avatar-icon-of-social-media-user-vector.jpg'
    db.session.commit()

    flash('Đã gỡ ảnh đại diện!', 'success')
    return redirect(url_for('user.profile_page'))


@user_bp.route('/upgrade-premium', methods=['POST'])
@login_required
def upgrade_premium():
    now = datetime.now()

    if current_user.is_premium and current_user.premium_until and current_user.premium_until > now:
        current_user.premium_until += timedelta(days=30)
    else:
        current_user.premium_until = now + timedelta(days=30)

    current_user.is_premium = True
    db.session.commit()

    flash(
        f'Thanh toán VNPay thành công! Gói PREMIUM của bạn có hạn đến {current_user.premium_until.strftime("%d/%m/%Y %H:%M")}.',
        'success')
    return redirect(url_for('user.profile_page'))


@user_bp.before_app_request
def check_premium_expiration():
    if current_user.is_authenticated and current_user.is_premium:
        if current_user.premium_until and datetime.now() > current_user.premium_until:
            current_user.is_premium = False
            current_user.premium_until = None
            db.session.commit()

            flash('Gói PREMIUM của bạn đã hết hạn. Hệ thống đã chuyển về gói FREE.', 'warning')

@user_bp.route('/history')
@login_required
def history_page():
    submissions = Submission.query.filter_by(user_id=current_user.id).order_by(Submission.id.desc()).all()

    history_data = []

    for sub in submissions:
        exercise_title = "Bài tập không xác định"

        if sub.skill == 'reading' or sub.skill == 'level_up_reading':
            exercise = ReadingExercise.query.get(sub.exercise_id)
            if exercise:
                exercise_title = exercise.title

        elif sub.skill == 'writing' or sub.skill == 'level_up_writing':
            exercise = WritingTopic.query.get(sub.exercise_id)
            if exercise:
                exercise_title = exercise.title

        history_data.append({
            'id': sub.id,
            'skill': sub.skill,
            'title': exercise_title,
            'score': sub.total_score
        })

    return render_template('student/history.html', history_data=history_data)