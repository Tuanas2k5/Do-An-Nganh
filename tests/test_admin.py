import pytest
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from extensions import db
from modules.users.models import User
from utils.utils import Role


@pytest.fixture
def admin_user(app, init_database):
    admin = User(
        first_name="Admin",
        last_name="Super",
        email="admin@learneng.com",
        phone="0901234567",
        password=generate_password_hash("Admin@123"),
        role=Role.ADMIN
    )
    db.session.add(admin)
    db.session.commit()
    return admin


def login_as(client, email, password="Password@123"):
    return client.post('/login', data={
        'email': email,
        'password': password
    }, follow_redirects=False)


# 1. DASHBOARD
def test_admin_dashboard_unauthenticated(client):
    response = client.get('/admin/dashboard', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_admin_dashboard_forbidden_for_student(client, init_database):
    login_as(client, 'test@learneng.com', 'Tuan@123')
    response = client.get('/admin/dashboard', follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['Location'] == '/'


def test_admin_dashboard_success(client, admin_user):
    login_as(client, admin_user.email, "Admin@123")
    response = client.get('/admin/dashboard')
    assert response.status_code == 200
    assert "Bảng Điều Khiển Quản Trị Viên" in response.text


# 2. CREATE TEACHER
def test_create_teacher_forbidden_for_non_admin(client, init_database):
    login_as(client, 'test@learneng.com', 'Tuan@123')
    response = client.post('/admin/create-teacher', data={
        'first_name': 'Van',
        'last_name': 'Nguyen',
        'email': 'teacher_new@learneng.com',
        'phone': '0912345678',
        'password': 'Password@123'
    }, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['Location'] == '/'


def test_create_teacher_invalid_name(client, admin_user):
    login_as(client, admin_user.email, "Admin@123")
    
    # Invalid first_name
    response = client.post('/admin/create-teacher', data={
        'first_name': 'A',  # too short
        'last_name': 'Nguyen',
        'email': 'teacher_new@learneng.com',
        'phone': '0912345678',
        'password': 'Password@123'
    }, follow_redirects=True)
    assert 'Tên không hợp lệ' in response.text

    # Invalid last_name
    response = client.post('/admin/create-teacher', data={
        'first_name': 'An',
        'last_name': '1',  # invalid char / too short
        'email': 'teacher_new@learneng.com',
        'phone': '0912345678',
        'password': 'Password@123'
    }, follow_redirects=True)
    assert 'Họ không hợp lệ' in response.text


def test_create_teacher_invalid_email(client, admin_user):
    login_as(client, admin_user.email, "Admin@123")
    response = client.post('/admin/create-teacher', data={
        'first_name': 'An',
        'last_name': 'Nguyen',
        'email': 'invalid-email',
        'phone': '0912345678',
        'password': 'Password@123'
    }, follow_redirects=True)
    assert 'Định dạng email không hợp lệ' in response.text


def test_create_teacher_duplicate_email(client, admin_user, init_database):
    login_as(client, admin_user.email, "Admin@123")
    response = client.post('/admin/create-teacher', data={
        'first_name': 'An',
        'last_name': 'Nguyen',
        'email': 'test@learneng.com',  # already exists
        'phone': '0912345678',
        'password': 'Password@123'
    }, follow_redirects=True)
    assert 'đã được sử dụng' in response.text


def test_create_teacher_invalid_phone(client, admin_user):
    login_as(client, admin_user.email, "Admin@123")
    response = client.post('/admin/create-teacher', data={
        'first_name': 'An',
        'last_name': 'Nguyen',
        'email': 'teacher_ok@learneng.com',
        'phone': '12345',  # invalid phone
        'password': 'Password@123'
    }, follow_redirects=True)
    assert 'Số điện thoại không hợp lệ' in response.text


def test_create_teacher_weak_password(client, admin_user):
    login_as(client, admin_user.email, "Admin@123")
    response = client.post('/admin/create-teacher', data={
        'first_name': 'An',
        'last_name': 'Nguyen',
        'email': 'teacher_ok@learneng.com',
        'phone': '0912345678',
        'password': '123'  # weak
    }, follow_redirects=True)
    assert 'Mật khẩu chưa đủ mạnh' in response.text


def test_create_teacher_success(client, admin_user):
    login_as(client, admin_user.email, "Admin@123")
    response = client.post('/admin/create-teacher', data={
        'first_name': 'Hoa',
        'last_name': 'Tran',
        'email': 'teacher_hoa@learneng.com',
        'phone': '0912345678',
        'password': 'Password@123'
    }, follow_redirects=True)
    assert 'Đã cấp tài khoản Giáo viên thành công' in response.text
    created = User.query.filter_by(email='teacher_hoa@learneng.com').first()
    assert created is not None
    assert created.role == Role.TEACHER


# 3. GIFT PREMIUM
def test_gift_premium_forbidden_for_non_admin(client, init_database):
    login_as(client, 'test@learneng.com', 'Tuan@123')
    response = client.post('/admin/gift-premium', data={'student_email': 'test@learneng.com'}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['Location'] == '/'


def test_gift_premium_user_not_found(client, admin_user):
    login_as(client, admin_user.email, "Admin@123")
    response = client.post('/admin/gift-premium', data={'student_email': 'notfound@learneng.com'}, follow_redirects=True)
    assert 'Không tìm thấy tài khoản nào' in response.text


def test_gift_premium_target_not_student(client, admin_user):
    login_as(client, admin_user.email, "Admin@123")
    response = client.post('/admin/gift-premium', data={'student_email': admin_user.email}, follow_redirects=True)
    assert 'Chỉ có thể tặng gói PREMIUM cho tài khoản Học sinh' in response.text


def test_gift_premium_success_free_user(client, admin_user, init_database):
    login_as(client, admin_user.email, "Admin@123")
    student = User.query.filter_by(email='test@learneng.com').first()
    assert student.is_premium is False

    response = client.post('/admin/gift-premium', data={'student_email': student.email}, follow_redirects=True)
    assert 'Đã kích hoạt gói PREMIUM 30 ngày thành công' in response.text
    db.session.refresh(student)
    assert student.is_premium is True
    assert student.premium_until is not None


def test_gift_premium_success_existing_premium_user(client, admin_user, init_database):
    student = User.query.filter_by(email='test@learneng.com').first()
    student.is_premium = True
    future_date = datetime.now() + timedelta(days=10)
    student.premium_until = future_date
    db.session.commit()

    login_as(client, admin_user.email, "Admin@123")
    response = client.post('/admin/gift-premium', data={'student_email': student.email}, follow_redirects=True)
    assert 'Đã kích hoạt gói PREMIUM 30 ngày thành công' in response.text
    db.session.refresh(student)
    assert student.premium_until > future_date + timedelta(days=29)


# 4. UPDATE LEVEL
def test_update_level_forbidden_for_non_admin(client, init_database):
    login_as(client, 'test@learneng.com', 'Tuan@123')
    response = client.post('/admin/update-level', data={
        'student_email': 'test@learneng.com',
        'new_level': 'B2',
        'reset_pp': 'yes'
    }, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['Location'] == '/'


def test_update_level_invalid_level(client, admin_user):
    login_as(client, admin_user.email, "Admin@123")
    response = client.post('/admin/update-level', data={
        'student_email': 'test@learneng.com',
        'new_level': 'INVALID',
        'reset_pp': 'no'
    }, follow_redirects=True)
    assert 'Cấp độ không hợp lệ' in response.text


def test_update_level_student_not_found(client, admin_user):
    login_as(client, admin_user.email, "Admin@123")
    response = client.post('/admin/update-level', data={
        'student_email': 'nobody@learneng.com',
        'new_level': 'B1',
        'reset_pp': 'no'
    }, follow_redirects=True)
    assert 'Không tìm thấy học sinh nào' in response.text


def test_update_level_target_not_student(client, admin_user):
    login_as(client, admin_user.email, "Admin@123")
    response = client.post('/admin/update-level', data={
        'student_email': admin_user.email,
        'new_level': 'B1',
        'reset_pp': 'no'
    }, follow_redirects=True)
    assert 'Nghiệp vụ này chỉ áp dụng cho tài khoản Học sinh' in response.text


def test_update_level_success_with_reset_pp(client, admin_user, init_database):
    student = User.query.filter_by(email='test@learneng.com').first()
    student.current_level = 'A1'
    student.progress_points = 80
    db.session.commit()

    login_as(client, admin_user.email, "Admin@123")
    response = client.post('/admin/update-level', data={
        'student_email': student.email,
        'new_level': 'B1',
        'reset_pp': 'yes'
    }, follow_redirects=True)
    assert 'Thành công! Đã chuyển học sinh' in response.text
    db.session.refresh(student)
    assert student.current_level == 'B1'
    assert student.progress_points == 0


def test_update_level_success_without_reset_pp(client, admin_user, init_database):
    student = User.query.filter_by(email='test@learneng.com').first()
    student.current_level = 'A1'
    student.progress_points = 80
    db.session.commit()

    login_as(client, admin_user.email, "Admin@123")
    response = client.post('/admin/update-level', data={
        'student_email': student.email,
        'new_level': 'A2',
        'reset_pp': 'no'
    }, follow_redirects=True)
    assert 'Thành công! Đã chuyển học sinh' in response.text
    db.session.refresh(student)
    assert student.current_level == 'A2'
    assert student.progress_points == 80
