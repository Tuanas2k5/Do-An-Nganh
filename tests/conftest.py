import pytest, os
from werkzeug.security import generate_password_hash
from __init__ import create_app
from extensions import db
from modules.users.models import User
from sqlalchemy.pool import StaticPool
from index import index, profile

os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

@pytest.fixture
def app():
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_ENGINE_OPTIONS": {
            "poolclass": StaticPool,
            "connect_args": {"check_same_thread": False}
        },
        "WTF_CSRF_ENABLED": False,
        "JWT_SECRET_KEY": "test-secret-key-that-is-at-least-32-bytes-long!",
        "JWT_COOKIE_CSRF_PROTECT": False
    }
    app = create_app(test_config)

    if 'index' not in app.view_functions:
        app.add_url_rule('/', 'index', index)
    if 'user.profile_page' not in app.view_functions:
        app.add_url_rule('/profile', 'user.profile_page', profile)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def init_database(app):
    hashed_password = generate_password_hash("Tuan@123")
    user = User(
        first_name="Học sinh",
        last_name="Test",
        email="test@learneng.com",
        phone="0123456789",
        password=hashed_password,
        hearts_count=5
    )
    db.session.add(user)
    db.session.commit()
    return user

# pytest --cov=modules tests/ --cov-report=term-missing