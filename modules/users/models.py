from flask_login import UserMixin
from extensions import db, login_manager
from utils.utils import Role


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.Enum(Role), nullable=False, default=Role.USER)
    active = db.Column(db.Boolean, nullable=False, default=True)
    progress_points = db.Column(db.Integer, nullable=False, default=0)

    is_premium = db.Column(db.Boolean, nullable=False, default=False)
    hearts_count = db.Column(db.Integer, nullable=False, default=5)
    last_heart_update = db.Column(db.DateTime, default=db.func.current_timestamp())

    current_level = db.Column(db.String(2), nullable=False, default='A1')
    has_done_placement = db.Column(db.Boolean, nullable=False, default=False)

    @property
    def is_active(self):
        return self.active


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))