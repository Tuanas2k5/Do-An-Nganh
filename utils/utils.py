import enum
from extensions import db

class Role(enum.Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


def check_level_up_eligibility(user):
    thresholds = {
        'A1': 100,
        'A2': 150,
        'B1': 200,
        'B2': 250,
        'C1': 300,
        'C2': float('inf')
    }

    current_threshold = thresholds.get(user.current_level, 0)

    return user.progress_points >= current_threshold