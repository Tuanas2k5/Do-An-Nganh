from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from modules.users.models import User
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt, set_access_cookies, unset_jwt_cookies, create_refresh_token, set_refresh_cookies
from flask_login import login_user

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Email hoặc mật khẩu không chính xác"}), 401

    if not user.active:
        return jsonify({"msg": "Tài khoản của bạn đã bị vô hiệu hóa"}), 403

    login_user(user)

    additional_claims = {"role": user.role.value}
    access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=str(user.id), additional_claims=additional_claims)

    response = jsonify({
        "msg": "Đăng nhập thành công",
        "role": user.role.value
    })

    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)

    return response, 200

@auth_bp.route('/api/logout', methods=['POST'])
def api_logout():
    response = jsonify({"msg": "Đăng xuất thành công"})
    unset_jwt_cookies(response)
    return response, 200


@auth_bp.route('/api/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    current_user_id = get_jwt_identity()

    user = User.query.get(current_user_id)
    if not user or not user.active:
        return jsonify({"msg": "Tài khoản không hợp lệ"}), 403

    additional_claims = {"role": user.role.value}

    new_access_token = create_access_token(identity=user.id, additional_claims=additional_claims)

    response = jsonify({"msg": "Token đã được làm mới thành công"})
    set_access_cookies(response, new_access_token)

    return response, 200

# @auth_bp.route('/api/login', methods=['POST'])
# def login():
#     email = request.json.get('email', None)
#     password = request.json.get('password', None)
#
#     user = User.query.filter_by(email=email).first()
#
#     if not user or not check_password_hash(user.password, password):
#         return jsonify({"msg": "Email hoặc mật khẩu không chính xác"}), 401
#
#     # Đính kèm vai trò vào Token để dễ dàng phân luồng (Học sinh/Giáo viên/Admin)
#     additional_claims = {"role": user.role.value}
#
#     # Tạo Token với định danh là ID của user
#     access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
#
#     return jsonify(access_token=access_token), 200


@auth_bp.route('/api/dashboard', methods=['GET'])
@jwt_required()
def protected_dashboard():
    current_user_id = get_jwt_identity()

    claims = get_jwt()
    user_role = claims.get("role")

    return jsonify(
        id=current_user_id,
        role=user_role,
        message="Xác thực JWT thành công! Chào mừng bạn đến hệ thống."
    ), 200

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

