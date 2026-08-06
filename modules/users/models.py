from flask_login import UserMixin
from extensions import db
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

    @property
    def is_active(self):
        return True