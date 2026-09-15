from flask_login import UserMixin
from extensions import db, login_manager
from utils.utils import Role
from datetime import datetime


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.Enum(Role), nullable=False, default=Role.STUDENT)
    active = db.Column(db.Boolean, nullable=False, default=True)
    progress_points = db.Column(db.Integer, nullable=False, default=0)

    is_premium = db.Column(db.Boolean, nullable=False, default=False)
    premium_until = db.Column(db.DateTime, nullable=True)
    hearts_count = db.Column(db.Integer, nullable=False, default=5)
    last_heart_update = db.Column(db.DateTime, default=db.func.current_timestamp())

    current_level = db.Column(db.String(2), nullable=False, default='A1')
    has_done_placement = db.Column(db.Boolean, nullable=False, default=False)

    avatar = db.Column(db.String(255), default='https://res.cloudinary.com/dwfzctwmt/image/upload/v1787924401/default-avatar-icon-of-social-media-user-vector.jpg')

    @property
    def is_active(self):
        return self.active

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(255), nullable=True)  # Đường dẫn khi học sinh click vào thông báo
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    user = db.relationship('User', backref=db.backref('notifications', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))