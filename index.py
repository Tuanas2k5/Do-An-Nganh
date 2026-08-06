from datetime import datetime
from flask import Flask, render_template
from __init__ import create_app
from extensions import db
from modules.users.models import User

app = create_app()

@app.context_processor
def inject_now():
    return {'year': datetime.now().year}

@app.route('/login', methods=['GET', 'POST'], endpoint='user.login_page')
def login():
    return render_template('login.html')

@app.route('/register', endpoint='user.register_page')
def register():
    return "Trang đăng ký (Đang xây dựng)"

@app.route('/profile', endpoint='user.profile_page')
def profile():
    return "Trang cá nhân (Đang xây dựng)"

@app.route('/logout', endpoint='user.logout')
def logout():
    return "Đăng xuất"

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)