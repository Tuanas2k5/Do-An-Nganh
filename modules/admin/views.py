import re
from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import current_user
from werkzeug.security import generate_password_hash
from extensions import db
from modules.users.models import User
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from extensions import db
from utils.utils import Role
from modules.users.models import User
from datetime import datetime, timedelta
from utils.validators import is_valid_name, validate_name_length, is_validate_email, validate_phone_number, validate_password_strength

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != Role.ADMIN:
        flash('Bạn không có quyền truy cập khu vực này!', 'danger')
        return redirect(url_for('index'))

    return render_template('admin/dashboard.html',
                           total_students=0,
                           total_teachers=0,
                           total_premium=0,
                           total_revenue=0)

@admin_bp.route('/create-teacher', methods=['POST'])
@login_required
def create_teacher():
    if current_user.role != Role.ADMIN:
        flash('Lỗi phân quyền: Chỉ Quản trị viên mới được thực hiện chức năng này!', 'danger')
        return redirect(url_for('index'))

    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', '')

    if not (is_valid_name(first_name) and validate_name_length(first_name)):
        flash('Tên không hợp lệ hoặc quá ngắn (tối thiểu 2 ký tự, không chứa số).', 'warning')
        return redirect(url_for('admin.dashboard'))

    if not (is_valid_name(last_name) and validate_name_length(last_name)):
        flash('Họ không hợp lệ hoặc quá ngắn.', 'warning')
        return redirect(url_for('admin.dashboard'))

    if not is_validate_email(email):
        flash('Định dạng email không hợp lệ!', 'warning')
        return redirect(url_for('admin.dashboard'))

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash(f'Email {email} đã được sử dụng. Vui lòng chọn email khác!', 'danger')
        return redirect(url_for('admin.dashboard'))

    if not validate_phone_number(phone):
        flash('Số điện thoại không hợp lệ (phải bắt đầu bằng số 0 và có đúng 10 chữ số).', 'warning')
        return redirect(url_for('admin.dashboard'))

    if not validate_password_strength(password):
        flash('Mật khẩu chưa đủ mạnh! Yêu cầu tối thiểu 8 ký tự, 1 chữ hoa, 1 chữ số và 1 ký tự đặc biệt.', 'warning')
        return redirect(url_for('admin.dashboard'))

    new_teacher = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        password=generate_password_hash(password),
        role=Role.TEACHER
    )

    db.session.add(new_teacher)
    db.session.commit()

    flash(f'Đã cấp tài khoản Giáo viên thành công cho {last_name} {first_name}.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/gift-premium', methods=['POST'])
@login_required
def gift_premium():
    if current_user.role != Role.ADMIN:
        flash('Lỗi phân quyền: Từ chối truy cập!', 'danger')
        return redirect(url_for('index'))

    student_email = request.form.get('student_email', '').strip()

    target_user = User.query.filter_by(email=student_email).first()

    if not target_user:
        flash(f'Không tìm thấy tài khoản nào đăng ký bằng email {student_email}.', 'danger')
        return redirect(url_for('admin.dashboard'))

    if target_user.role != Role.STUDENT:
        flash('Chỉ có thể tặng gói PREMIUM cho tài khoản Học sinh!', 'warning')
        return redirect(url_for('admin.dashboard'))

    now = datetime.now()
    if target_user.is_premium and target_user.premium_until and target_user.premium_until > now:
        target_user.premium_until += timedelta(days=30)
    else:
        target_user.premium_until = now + timedelta(days=30)

    target_user.is_premium = True
    db.session.commit()

    flash(f'Đã kích hoạt gói PREMIUM 30 ngày thành công cho học sinh {target_user.last_name} {target_user.first_name}!',
          'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/update-level', methods=['POST'])
@login_required
def update_level():
    if current_user.role != Role.ADMIN:
        flash('Lỗi phân quyền: Từ chối truy cập!', 'danger')
        return redirect(url_for('index'))

    student_email = request.form.get('student_email', '').strip()
    new_level = request.form.get('new_level')
    reset_pp = request.form.get('reset_pp')

    VALID_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
    if new_level not in VALID_LEVELS:
        flash('Cấp độ không hợp lệ!', 'danger')
        return redirect(url_for('admin.dashboard'))

    target_user = User.query.filter_by(email=student_email).first()

    if not target_user:
        flash(f'Không tìm thấy học sinh nào mang email {student_email}.', 'danger')
        return redirect(url_for('admin.dashboard'))

    if target_user.role != Role.STUDENT:
        flash('Nghiệp vụ này chỉ áp dụng cho tài khoản Học sinh!', 'warning')
        return redirect(url_for('admin.dashboard'))

    old_level = target_user.current_level
    target_user.current_level = new_level

    if reset_pp == 'yes':
        target_user.progress_points = 0

    db.session.commit()

    flash(
        f'Thành công! Đã chuyển học sinh {target_user.last_name} {target_user.first_name} từ {old_level} sang {new_level}.',
        'success')
    return redirect(url_for('admin.dashboard'))