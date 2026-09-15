import re
from email_validator import validate_email, EmailNotValidError

def is_valid_name(name):
    if not name:
        return False
    name_pattern = re.compile(r'^[^\W\d_]+(\s+[^\W\d_]+)*$')
    return bool(name_pattern.match(name.strip()))

def validate_password_strength(password):
    pw_pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[!#&*\_\-@]).{8,}$'
    return bool(re.match(pw_pattern, password))

def validate_phone_number(phone):
    phone_pattern = r'^0\d{9}$'
    return bool(re.match(phone_pattern, phone))

def is_validate_email(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

def validate_name_length(name):
    return len(name.strip()) >= 2