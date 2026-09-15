import io
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from werkzeug.security import generate_password_hash

from extensions import db
from modules.users.models import User
from modules.users.services import register_new_user, verify_user_login
from modules.exams.models import Submission, ReadingExercise, WritingTopic
from utils.utils import Role


def test_user_model_creation(app, init_database):
    user = User.query.filter_by(email="test@learneng.com").first()

    assert user is not None
    assert user.hearts_count == 5
    assert user.current_level == 'A1'
    assert user.is_active is True


def test_register_new_user_service_success(app, init_database):
    data = {
        'first_name': 'Nguyen',
        'last_name': 'An',
        'email': 'nguyenan@gmail.com',
        'phone': '0987654321',
        'password': 'Password@123',
        'confirm_password': 'Password@123'
    }
    success, message = register_new_user(data)
    assert success is True
    assert 'thành công' in message

    created_user = User.query.filter_by(email='nguyenan@gmail.com').first()
    assert created_user is not None
    assert created_user.first_name == 'Nguyen'


def test_register_new_user_service_password_mismatch(app, init_database):
    data = {
        'first_name': 'Nguyen',
        'last_name': 'B',
        'email': 'nguyenb@gmail.com',
        'phone': '0987654321',
        'password': 'Password@123',
        'confirm_password': 'DifferentPassword'
    }
    success, message = register_new_user(data)
    assert success is False
    assert message == 'Mật khẩu xác nhận không khớp!'


def test_register_new_user_service_duplicate_email(app, init_database):
    data = {
        'first_name': 'Duplicate',
        'last_name': 'User',
        'email': 'test@learneng.com',
        'phone': '0987654321',
        'password': 'Password@123',
        'confirm_password': 'Password@123'
    }
    success, message = register_new_user(data)
    assert success is False
    assert 'đã được sử dụng' in message


def test_register_new_user_service_exception(app, init_database):
    data = {
        'first_name': 'Err',
        'last_name': 'Test',
        'email': 'err@gmail.com',
        'phone': '0987654321',
        'password': 'Password@123',
        'confirm_password': 'Password@123'
    }
    with patch('extensions.db.session.commit', side_effect=Exception('DB Error')):
        success, message = register_new_user(data)
        assert success is False
        assert 'Đã xảy ra lỗi hệ thống' in message


def test_verify_user_login_service(app, init_database):
    success, user = verify_user_login('test@learneng.com', 'Tuan@123')
    assert success is True
    assert user is not None
    assert user.email == 'test@learneng.com'

    success_wrong_pass, user_wrong_pass = verify_user_login('test@learneng.com', 'WrongPass')
    assert success_wrong_pass is False
    assert user_wrong_pass is None

    success_wrong_email, user_wrong_email = verify_user_login('nonexistent@learneng.com', 'Tuan@123')
    assert success_wrong_email is False
    assert user_wrong_email is None


def test_login_api_success(client, init_database):
    response = client.post('/api/login', json={
        'email': 'test@learneng.com',
        'password': 'Tuan@123'
    })

    assert response.status_code == 200, f"Lỗi login thất bại: {response.get_json()}"
    assert response.json.get("msg") == "Đăng nhập thành công"
    assert response.json.get("role") == Role.STUDENT.value


def test_login_api_failure(client, init_database):
    response = client.post('/api/login', json={
        'email': 'test@learneng.com',
        'password': 'WrongPassword'
    })

    assert response.status_code == 401
    assert "không chính xác" in response.json['msg']


def test_login_api_inactive_user(client, init_database):
    user = User.query.filter_by(email='test@learneng.com').first()
    user.active = False
    db.session.commit()

    response = client.post('/api/login', json={
        'email': 'test@learneng.com',
        'password': 'Tuan@123'
    })

    assert response.status_code == 403
    assert "vô hiệu hóa" in response.json['msg']


def test_logout_api(client, init_database):
    client.post('/api/login', json={
        'email': 'test@learneng.com',
        'password': 'Tuan@123'
    })

    response = client.post('/api/logout')
    assert response.status_code == 200
    assert response.json.get('msg') == "Đăng xuất thành công"


def test_protected_dashboard_api_success(client, init_database):
    client.post('/api/login', json={
        'email': 'test@learneng.com',
        'password': 'Tuan@123'
    })

    response = client.get('/api/dashboard')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data.get('role') == Role.STUDENT.value
    assert "Xác thực JWT thành công" in json_data.get('message')


def test_protected_dashboard_api_unauthorized(client):
    response = client.get('/api/dashboard')
    assert response.status_code == 401


def test_refresh_token_api_success(client, init_database):
    login_res = client.post('/api/login', json={
        'email': 'test@learneng.com',
        'password': 'Tuan@123'
    })
    assert login_res.status_code == 200

    response = client.post('/api/refresh')
    assert response.status_code == 200
    assert "làm mới thành công" in response.json.get('msg')


def test_refresh_token_api_inactive_user(client, init_database):
    client.post('/api/login', json={
        'email': 'test@learneng.com',
        'password': 'Tuan@123'
    })

    user = User.query.filter_by(email='test@learneng.com').first()
    user.active = False
    db.session.commit()

    response = client.post('/api/refresh')
    assert response.status_code == 403
    assert "không hợp lệ" in response.json.get('msg')



def test_register_page_get(client):
    response = client.get('/register')
    assert response.status_code == 200


def test_register_page_post_success(client, init_database):
    response = client.post('/register', data={
        'first_name': 'New',
        'last_name': 'User',
        'email': 'newuser@learneng.com',
        'phone': '0112233445',
        'password': 'Password@123',
        'confirm_password': 'Password@123'
    }, follow_redirects=False)

    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_register_page_post_failure(client, init_database):
    response = client.post('/register', data={
        'first_name': 'New',
        'last_name': 'User',
        'email': 'newuser@learneng.com',
        'phone': '0112233445',
        'password': 'Password@123',
        'confirm_password': 'WrongConfirmPassword'
    })

    assert response.status_code == 200


def test_login_page_get(client):
    response = client.get('/login')
    assert response.status_code == 200


def test_login_page_post_student_success(client, init_database):
    response = client.post('/login', data={
        'email': 'test@learneng.com',
        'password': 'Tuan@123'
    }, follow_redirects=False)

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/') or response.headers['Location'] == '/'


def test_login_page_post_teacher_success(client, init_database):
    teacher = User(
        first_name="Giaoviên",
        last_name="Test",
        email="teacher@learneng.com",
        phone="0999888777",
        password=generate_password_hash("Password@123"),
        role=Role.TEACHER
    )
    db.session.add(teacher)
    db.session.commit()

    response = client.post('/login', data={
        'email': 'teacher@learneng.com',
        'password': 'Password@123'
    }, follow_redirects=False)

    assert response.status_code == 302
    assert '/teacher' in response.headers['Location']


def test_login_page_post_admin_success(client, init_database):
    admin = User(
        first_name="Admin",
        last_name="Test",
        email="admin@learneng.com",
        phone="0999888777",
        password=generate_password_hash("Password@123"),
        role=Role.ADMIN
    )
    db.session.add(admin)
    db.session.commit()

    response = client.post('/login', data={
        'email': 'admin@learneng.com',
        'password': 'Password@123'
    }, follow_redirects=False)

    assert response.status_code == 302
    assert '/admin' in response.headers['Location']


def test_login_page_post_failure(client, init_database):
    response = client.post('/login', data={
        'email': 'test@learneng.com',
        'password': 'WrongPassword'
    })

    assert response.status_code == 200


def test_logout_view(client, init_database):
    client.post('/login', data={
        'email': 'test@learneng.com',
        'password': 'Tuan@123'
    })

    response = client.get('/logout', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_logout_view_unauthenticated(client):
    response = client.get('/logout', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_upload_avatar_no_file(client, init_database):
    client.post('/login', data={
        'email': 'test@learneng.com',
        'password': 'Tuan@123'
    })

    response = client.post('/profile/avatar', follow_redirects=False)
    assert response.status_code == 302


def test_upload_avatar_empty_filename(client, init_database):
    client.post('/login', data={
        'email': 'test@learneng.com',
        'password': 'Tuan@123'
    })

    data = {
        'avatar': (io.BytesIO(b""), '')
    }
    response = client.post('/profile/avatar', data=data, content_type='multipart/form-data', follow_redirects=False)
    assert response.status_code == 302


@patch('modules.users.views.cloudinary.uploader.upload')
def test_upload_avatar_success(mock_upload, client, init_database):
    mock_upload.return_value = {'secure_url': 'https://cloudinary.com/test_avatar.jpg'}

    client.post('/login', data={
        'email': 'test@learneng.com',
        'password': 'Tuan@123'
    })

    data = {
        'avatar': (io.BytesIO(b"dummy image data"), 'test.jpg')
    }
    response = client.post('/profile/avatar', data=data, content_type='multipart/form-data', follow_redirects=False)
    assert response.status_code == 302

    user = User.query.filter_by(email='test@learneng.com').first()
    assert user.avatar == 'https://cloudinary.com/test_avatar.jpg'


@patch('modules.users.views.cloudinary.uploader.upload')
def test_upload_avatar_exception(mock_upload, client, init_database):
    mock_upload.side_effect = Exception("Cloudinary connection error")

    client.post('/login', data={
        'email': 'test@learneng.com',
        'password': 'Tuan@123'
    })

    data = {
        'avatar': (io.BytesIO(b"dummy image data"), 'test.jpg')
    }
    response = client.post('/profile/avatar', data=data, content_type='multipart/form-data', follow_redirects=False)
    assert response.status_code == 302


def test_remove_avatar(client, init_database):
    client.post('/login', data={
        'email': 'test@learneng.com',
        'password': 'Tuan@123'
    })

    user = User.query.filter_by(email='test@learneng.com').first()
    user.avatar = 'https://cloudinary.com/custom.jpg'
    db.session.commit()

    response = client.post('/profile/avatar/remove', follow_redirects=False)
    assert response.status_code == 302

    user = User.query.filter_by(email='test@learneng.com').first()
    assert 'default-avatar' in user.avatar


def test_upgrade_premium(client, init_database):
    client.post('/login', data={
        'email': 'test@learneng.com',
        'password': 'Tuan@123'
    })

    # Nâng cấp premium lần đầu
    response = client.post('/upgrade-premium', follow_redirects=False)
    assert response.status_code == 302

    user = User.query.filter_by(email='test@learneng.com').first()
    assert user.is_premium is True
    assert user.premium_until is not None
    first_expiration = user.premium_until

    # Gia hạn premium lần hai (+30 ngày)
    response_extend = client.post('/upgrade-premium', follow_redirects=False)
    assert response_extend.status_code == 302

    user = User.query.filter_by(email='test@learneng.com').first()
    assert user.premium_until > first_expiration


def test_check_premium_expiration(client, init_database):
    client.post('/login', data={
        'email': 'test@learneng.com',
        'password': 'Tuan@123'
    })

    user = User.query.filter_by(email='test@learneng.com').first()
    user.is_premium = True
    user.premium_until = datetime.now() - timedelta(days=1)
    db.session.commit()

    # Bất kỳ request nào cũng kích hoạt middleware check_premium_expiration
    client.get('/history')

    updated_user = User.query.filter_by(email='test@learneng.com').first()
    assert updated_user.is_premium is False
    assert updated_user.premium_until is None


def test_history_page(client, init_database):
    client.post('/login', data={
        'email': 'test@learneng.com',
        'password': 'Tuan@123'
    })

    user = User.query.filter_by(email='test@learneng.com').first()

    reading_ex = ReadingExercise(title="Bài đọc IELTS 1", content="Content", level="A1", created_by=user.id)
    writing_topic = WritingTopic(title="Bài viết IELTS 1", description="Description", level="A1", created_by=user.id)
    db.session.add_all([reading_ex, writing_topic])
    db.session.commit()

    sub1 = Submission(user_id=user.id, skill='reading', exercise_id=reading_ex.id, total_score=8.5)
    sub2 = Submission(user_id=user.id, skill='writing', exercise_id=writing_topic.id, total_score=7.0)
    sub3 = Submission(user_id=user.id, skill='unknown_skill', exercise_id=999, total_score=5.0)
    db.session.add_all([sub1, sub2, sub3])
    db.session.commit()

    response = client.get('/history')
    assert response.status_code == 200