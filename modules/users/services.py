from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from .models import User

def register_new_user(data):
    if data['password'] != data['confirm_password']:
        return False, 'Mật khẩu xác nhận không khớp!'

    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return False, 'Email này đã được sử dụng! Vui lòng dùng email khác.'

    try:
        hashed_password = generate_password_hash(data['password'])
        new_user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data['phone'],
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        return True, 'Đăng ký tài khoản thành công! Vui lòng đăng nhập.'
    except Exception as e:
        db.session.rollback()
        return False, f'Đã xảy ra lỗi hệ thống: {str(e)}'

def verify_user_login(email, password):
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        return True, user
    return False, None