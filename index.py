from datetime import datetime
from flask import Flask, render_template, redirect, url_for
from __init__ import create_app
from extensions import db
from modules.exams.models import ReadingExercise, WritingTopic
from modules.users.models import User, Notification
from flask_login import current_user
from seed import seed_initial_data

app = create_app()

@app.context_processor
def inject_now():
    return {'year': datetime.now().year}

@app.route('/profile', endpoint='user.profile_page')
def profile():
    return render_template('profile.html')


@app.context_processor
def inject_notifications():
    if current_user.is_authenticated:
        recent_notifications = Notification.query.filter_by(user_id=current_user.id) \
            .order_by(Notification.id.desc()).limit(5).all()
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()

        return dict(
            recent_notifications=recent_notifications,
            unread_count=unread_count
        )
    return dict(recent_notifications=[], unread_count=0)


@app.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template('index.html')

    if not current_user.has_done_placement:
        return redirect(url_for('exams.placement_test_page'))

    thresholds = {
        'A1': 100,
        'A2': 150,
        'B1': 200,
        'B2': 250,
        'C1': 300,
        'C2': 'MAX'
    }
    pp_threshold = thresholds.get(current_user.current_level, 100)

    readings = ReadingExercise.query.filter_by(is_active=True).order_by(ReadingExercise.id.desc()).all()
    writings = WritingTopic.query.filter_by(is_active=True).order_by(WritingTopic.id.desc()).all()

    return render_template('student/dashboard.html',
                           readings=readings,
                           writings=writings,
                           pp_threshold=pp_threshold)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_initial_data()
    app.run(debug=True, port=5000)