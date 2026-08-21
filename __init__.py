import os
from flask import Flask
from urllib.parse import quote
from dotenv import find_dotenv, load_dotenv
from extensions import db, login_manager
from modules.users.models import User
from modules.exams.models import ReadingExercise, ReadingQuestion, WritingTopic, Submission
from modules.users.views import user_bp
from modules.exams.views import exams_bp
from modules.users import models

load_dotenv(find_dotenv())

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = (f"mysql+pymysql://"
                                             f"{os.getenv('DB_USER')}:"
                                             f"{quote(os.getenv('DB_PASSWORD'))}@localhost/"
                                             f"{os.getenv('DB_NAME')}?charset=utf8mb4")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    app.config["PAGE_SIZE"] = 2
    app.config["DEBUG"] = os.getenv("DEBUG_MODE")
    app.config["HOST"] = os.getenv("HOST", "127.0.0.1")
    app.config["PORT"] = 8000
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "user.login_page"
    login_manager.login_message = "Vui lòng đăng nhập để tiếp tục!"
    login_manager.login_message_category = "warning"

    app.register_blueprint(user_bp)
    app.register_blueprint(exams_bp)

    return app