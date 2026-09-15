from extensions import db
from datetime import datetime


class ReadingExercise(db.Model):
    __tablename__ = 'reading_exercises'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    level = db.Column(db.String(2), nullable=False)
    time_limit = db.Column(db.Integer, default=15)

    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='draft')
    is_active = db.Column(db.Boolean, default=True)
    version = db.Column(db.Integer, default=1)

    questions = db.relationship('ReadingQuestion', backref='exercise', lazy=True)


class ReadingQuestion(db.Model):
    __tablename__ = 'reading_questions'
    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('reading_exercises.id'),
                            nullable=True)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    level = db.Column(db.String(2), nullable=False)  #
    is_placement_test = db.Column(db.Boolean, default=False)


class StudentReadingAnswer(db.Model):
    __tablename__ = 'student_reading_answers'
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('reading_questions.id'), nullable=False)
    selected_option = db.Column(db.String(1), nullable=True)
    is_correct = db.Column(db.Boolean, default=False, nullable=False)
    submission = db.relationship('Submission',
                                 backref=db.backref('student_answers', lazy=True, cascade="all, delete-orphan"))
    question = db.relationship('ReadingQuestion',
                               backref=db.backref('student_answers', lazy=True, cascade="all, delete-orphan"))

class WritingTopic(db.Model):
    __tablename__ = 'writing_topics'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    level = db.Column(db.String(2), nullable=False)
    min_words = db.Column(db.Integer, nullable=False, default=150)
    max_words = db.Column(db.Integer, nullable=False, default=250)

    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='published')
    is_active = db.Column(db.Boolean, default=True)
    version = db.Column(db.Integer, default=1)


class Submission(db.Model):
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exercise_id = db.Column(db.Integer, nullable=True)
    skill = db.Column(db.String(20), nullable=False)  # 'reading', 'writing', 'placement'
    content_submitted = db.Column(db.Text, nullable=True)
    total_score = db.Column(db.Float, nullable=True)

    grammar_score = db.Column(db.Float, nullable=True)
    vocabulary_score = db.Column(db.Float, nullable=True)
    coherence_score = db.Column(db.Float, nullable=True)
    task_response_score = db.Column(db.Float, nullable=True)

    ai_feedback = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)