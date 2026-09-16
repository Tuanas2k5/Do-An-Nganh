import os
from flask import Flask
from flask_jwt_extended import JWTManager
from urllib.parse import quote
from dotenv import find_dotenv, load_dotenv
from extensions import db, login_manager
from modules.users.models import User
from modules.exams.models import ReadingExercise, ReadingQuestion, WritingTopic, Submission
from modules.users.services import auth_bp
from modules.users.views import user_bp
from modules.exams.views import exams_bp
from modules.admin.views import admin_bp
from modules.users import models
from modules.teacher.views import teacher_bp
import cloudinary
import cloudinary.uploader
from admin import setup_admin

load_dotenv(find_dotenv())

def create_app(config_override=None):
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "dev_secret")
    db_user = os.getenv('DB_USER', 'root')
    db_pass = quote(os.getenv('DB_PASSWORD', ''))
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '3306')
    db_name = os.getenv('DB_NAME', 'doan')
    default_db_uri = os.getenv('DATABASE_URL') or f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"

    app.config["SQLALCHEMY_DATABASE_URI"] = default_db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    app.config["PAGE_SIZE"] = 2
    app.config["DEBUG"] = os.getenv("DEBUG_MODE")
    app.config["HOST"] = os.getenv("HOST", "127.0.0.1")
    app.config["PORT"] = 8000
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev_secret")
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'my_jwt_secret_key')
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_SECURE'] = False
    app.config['JWT_COOKIE_CSRF_PROTECT'] = True

    app.config['JWT_ACCESS_CSRF_HEADER_NAME'] = 'X-CSRF-TOKEN'
    app.config['JWT_REFRESH_CSRF_HEADER_NAME'] = 'X-CSRF-TOKEN'

    if config_override:
        app.config.update(config_override)

    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_API_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRETKEY")
    )

    db.init_app(app)

    setup_admin(app)

    login_manager.init_app(app)
    login_manager.login_view = "user.login_page"
    login_manager.login_message = "Vui lòng đăng nhập để tiếp tục!"
    login_manager.login_message_category = "warning"

    app.register_blueprint(user_bp)
    app.register_blueprint(exams_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)

    jwt = JWTManager(app)

    # Tự động tạo bảng khi app khởi động (an toàn, chỉ tạo nếu chưa có)
    with app.app_context():
        db.create_all()

    return app