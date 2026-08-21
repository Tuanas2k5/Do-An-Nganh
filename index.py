from datetime import datetime
from flask import Flask, render_template, redirect, url_for
from __init__ import create_app
from extensions import db
from modules.exams.models import ReadingExercise, WritingTopic
from modules.users.models import User
from flask_login import current_user

app = create_app()

@app.context_processor
def inject_now():
    return {'year': datetime.now().year}

@app.route('/profile', endpoint='user.profile_page')
def profile():
    return "Trang cá nhân (Đang xây dựng)"


@app.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template('index.html')

    if not current_user.has_done_placement:
        return redirect(url_for('exams.placement_test_page'))

    available_reading = ReadingExercise.query.limit(3).all()
    available_writing = WritingTopic.query.limit(3).all()

    return render_template('dashboard.html',
                           readings=available_reading,
                           writings=available_writing)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)