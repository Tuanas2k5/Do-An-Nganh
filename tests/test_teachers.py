import pytest
from werkzeug.security import generate_password_hash
from extensions import db
from modules.users.models import User, Notification
from modules.exams.models import ReadingExercise, ReadingQuestion, WritingTopic, Submission
from utils.utils import Role


@pytest.fixture
def teacher_user(app, init_database):
    teacher = User(
        first_name="Teacher",
        last_name="One",
        email="teacher1@learneng.com",
        phone="0911223344",
        password=generate_password_hash("Password@123"),
        role=Role.TEACHER
    )
    db.session.add(teacher)
    db.session.commit()
    return teacher


@pytest.fixture
def other_teacher(app, init_database):
    teacher2 = User(
        first_name="Teacher",
        last_name="Two",
        email="teacher2@learneng.com",
        phone="0922334455",
        password=generate_password_hash("Password@123"),
        role=Role.TEACHER
    )
    db.session.add(teacher2)
    db.session.commit()
    return teacher2


def login_as(client, email, password="Password@123"):
    return client.post('/login', data={
        'email': email,
        'password': password
    }, follow_redirects=False)


# 1. DASHBOARD & PHÂN QUYỀN TRUY CẬP (RBAC)
def test_dashboard_unauthenticated(client):
    response = client.get('/teacher/dashboard', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_dashboard_forbidden_for_student(client, init_database):
    login_as(client, 'test@learneng.com', 'Tuan@123')
    response = client.get('/teacher/dashboard')
    assert response.status_code == 403


def test_dashboard_accessible_by_teacher(client, teacher_user):
    login_as(client, teacher_user.email)
    response = client.get('/teacher/dashboard')
    assert response.status_code == 200


# 2. QUẢN LÝ BÀI ĐỌC (READING EXERCISE)
def test_create_reading_draft_success(client, teacher_user):
    login_as(client, teacher_user.email)

    response = client.post('/teacher/reading/create', data={
        'title': 'IELTS Reading Cambridge 18',
        'level': 'B2',
        'time_limit': 60,
        'content': 'This is a sample reading passage.'
    }, follow_redirects=False)

    assert response.status_code == 302
    assert '/teacher/dashboard' in response.headers['Location']

    exercise = ReadingExercise.query.filter_by(title='IELTS Reading Cambridge 18').first()
    assert exercise is not None
    assert exercise.status == 'draft'
    assert exercise.version == 1
    assert exercise.created_by == teacher_user.id
    assert exercise.is_active is True


def test_create_reading_forbidden_for_student(client, init_database):
    login_as(client, 'test@learneng.com', 'Tuan@123')
    response = client.post('/teacher/reading/create', data={
        'title': 'Hacker Reading',
        'level': 'A1',
        'time_limit': 30,
        'content': 'Content'
    }, follow_redirects=False)

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/') or response.headers['Location'] == '/'
    assert ReadingExercise.query.filter_by(title='Hacker Reading').first() is None


def test_edit_reading_without_submissions(client, teacher_user):
    login_as(client, teacher_user.email)
    exercise = ReadingExercise(
        title='Old Title',
        content='Old Content',
        level='A2',
        time_limit=30,
        created_by=teacher_user.id,
        status='draft',
        version=1
    )
    db.session.add(exercise)
    db.session.commit()

    response = client.post(f'/teacher/reading/{exercise.id}/edit', data={
        'title': 'Updated Title',
        'level': 'B1',
        'time_limit': 45,
        'content': 'Updated Content'
    }, follow_redirects=False)

    assert response.status_code == 302
    db.session.refresh(exercise)
    assert exercise.title == 'Updated Title'
    assert exercise.level == 'B1'
    assert exercise.version == 1


def test_edit_reading_with_submissions_increments_version(client, teacher_user, init_database):
    login_as(client, teacher_user.email)
    exercise = ReadingExercise(
        title='Versioned Reading',
        content='Content',
        level='B1',
        time_limit=30,
        created_by=teacher_user.id,
        status='published',
        version=1
    )
    db.session.add(exercise)
    db.session.commit()

    submission = Submission(
        user_id=init_database.id,
        exercise_id=exercise.id,
        skill='reading',
        total_score=80.0
    )
    db.session.add(submission)
    db.session.commit()

    client.post(f'/teacher/reading/{exercise.id}/edit', data={
        'title': 'Versioned Reading v2',
        'level': 'B1',
        'time_limit': 35,
        'content': 'Modified Content'
    }, follow_redirects=False)

    db.session.refresh(exercise)
    assert exercise.version == 2


def test_delete_reading_without_submissions_hard_deletes(client, teacher_user):
    login_as(client, teacher_user.email)
    exercise = ReadingExercise(
        title='To Delete',
        content='Passage content',
        level='A1',
        created_by=teacher_user.id
    )
    db.session.add(exercise)
    db.session.commit()
    ex_id = exercise.id

    response = client.post(f'/teacher/reading/{ex_id}/delete', follow_redirects=False)
    assert response.status_code == 302
    assert ReadingExercise.query.get(ex_id) is None


def test_delete_reading_with_submissions_soft_deletes(client, teacher_user, init_database):
    login_as(client, teacher_user.email)
    exercise = ReadingExercise(
        title='Soft Delete',
        content='Passage content',
        level='A1',
        created_by=teacher_user.id,
        is_active=True
    )
    db.session.add(exercise)
    db.session.commit()

    sub = Submission(
        user_id=init_database.id,
        exercise_id=exercise.id,
        skill='reading',
        total_score=70.0
    )
    db.session.add(sub)
    db.session.commit()

    client.post(f'/teacher/reading/{exercise.id}/delete', follow_redirects=False)

    db.session.refresh(exercise)
    assert exercise.is_active is False
    assert ReadingExercise.query.get(exercise.id) is not None


def test_reading_actions_forbidden_for_other_teacher(client, teacher_user, other_teacher):
    exercise = ReadingExercise(
        title='Teacher1 Exercise',
        content='Passage content',
        level='A1',
        created_by=teacher_user.id
    )
    db.session.add(exercise)
    db.session.commit()

    login_as(client, other_teacher.email)

    # Thử sửa bài của giáo viên khác
    res_edit = client.post(f'/teacher/reading/{exercise.id}/edit', data={
        'title': 'Hacked Title',
        'level': 'A1',
        'time_limit': 20,
        'content': 'Hacked'
    }, follow_redirects=False)
    assert res_edit.status_code == 302
    db.session.refresh(exercise)
    assert exercise.title == 'Teacher1 Exercise'

    # Thử xóa bài của giáo viên khác
    res_delete = client.post(f'/teacher/reading/{exercise.id}/delete', follow_redirects=False)
    assert res_delete.status_code == 302
    assert ReadingExercise.query.get(exercise.id) is not None


# 3. QUẢN LÝ CÂU HỎI TRẮC NGHIỆM (READING QUESTIONS)
def test_add_reading_question(client, teacher_user):
    login_as(client, teacher_user.email)
    exercise = ReadingExercise(
        title='Reading Questions Test',
        content='Sample passage content',
        level='A2',
        created_by=teacher_user.id,
        status='draft'
    )
    db.session.add(exercise)
    db.session.commit()

    response = client.post(f'/teacher/reading/{exercise.id}/questions', data={
        'action': 'add_question',
        'content': 'Where is Paris?',
        'option_a': 'France',
        'option_b': 'Germany',
        'option_c': 'Italy',
        'option_d': 'Spain',
        'correct_answer': 'A'
    }, follow_redirects=False)

    assert response.status_code == 302
    question = ReadingQuestion.query.filter_by(exercise_id=exercise.id).first()
    assert question is not None
    assert question.question_text == 'Where is Paris?'
    assert question.correct_answer == 'A'
    assert question.level == 'A2'


def test_publish_reading_fails_when_under_5_questions(client, teacher_user):
    login_as(client, teacher_user.email)
    exercise = ReadingExercise(
        title='Short Test',
        content='Sample passage content',
        level='A1',
        created_by=teacher_user.id,
        status='draft'
    )
    db.session.add(exercise)
    db.session.commit()

    # Thêm 2 câu hỏi (chưa đủ 5 câu)
    for i in range(2):
        q = ReadingQuestion(
            exercise_id=exercise.id,
            question_text=f'Q{i}',
            option_a='1', option_b='2', option_c='3', option_d='4',
            correct_answer='A',
            level='A1'
        )
        db.session.add(q)
    db.session.commit()

    response = client.post(f'/teacher/reading/{exercise.id}/questions', data={
        'action': 'publish'
    }, follow_redirects=False)

    assert response.status_code == 302
    assert f'/teacher/reading/{exercise.id}/questions' in response.headers['Location']
    db.session.refresh(exercise)
    assert exercise.status == 'draft'


def test_publish_reading_success_when_at_least_5_questions(client, teacher_user):
    login_as(client, teacher_user.email)
    exercise = ReadingExercise(
        title='Ready Test',
        content='Sample passage content',
        level='A1',
        created_by=teacher_user.id,
        status='draft'
    )
    db.session.add(exercise)
    db.session.commit()

    for i in range(5):
        q = ReadingQuestion(
            exercise_id=exercise.id,
            question_text=f'Question {i+1}',
            option_a='A', option_b='B', option_c='C', option_d='D',
            correct_answer='A',
            level='A1'
        )
        db.session.add(q)
    db.session.commit()

    response = client.post(f'/teacher/reading/{exercise.id}/questions', data={
        'action': 'publish'
    }, follow_redirects=False)

    assert response.status_code == 302
    assert '/teacher/dashboard' in response.headers['Location']
    db.session.refresh(exercise)
    assert exercise.status == 'published'


def test_delete_reading_question_reverts_published_to_draft(client, teacher_user):
    login_as(client, teacher_user.email)
    exercise = ReadingExercise(
        title='Published Reading',
        content='Sample passage content',
        level='A1',
        created_by=teacher_user.id,
        status='published'
    )
    db.session.add(exercise)
    db.session.commit()

    q = ReadingQuestion(
        exercise_id=exercise.id,
        question_text='To be deleted',
        option_a='1', option_b='2', option_c='3', option_d='4',
        correct_answer='B',
        level='A1'
    )
    db.session.add(q)
    db.session.commit()
    q_id = q.id

    response = client.post(f'/teacher/reading/{exercise.id}/questions/{q_id}/delete', follow_redirects=False)
    assert response.status_code == 302

    db.session.refresh(exercise)
    assert exercise.status == 'draft'
    assert ReadingQuestion.query.get(q_id) is None


def test_edit_reading_question_with_submissions_increments_exercise_version(client, teacher_user, init_database):
    login_as(client, teacher_user.email)
    exercise = ReadingExercise(
        title='Exercise with Subs',
        content='Sample passage content',
        level='B1',
        created_by=teacher_user.id,
        version=1
    )
    db.session.add(exercise)
    db.session.commit()

    q = ReadingQuestion(
        exercise_id=exercise.id,
        question_text='Original Q',
        option_a='A', option_b='B', option_c='C', option_d='D',
        correct_answer='A',
        level='B1'
    )
    sub = Submission(
        user_id=init_database.id,
        exercise_id=exercise.id,
        skill='reading',
        total_score=100.0
    )
    db.session.add_all([q, sub])
    db.session.commit()

    response = client.post(f'/teacher/reading/{exercise.id}/questions/{q.id}/edit', data={
        'content': 'Edited Q',
        'option_a': 'A*',
        'option_b': 'B*',
        'option_c': 'C*',
        'option_d': 'D*',
        'correct_answer': 'C'
    }, follow_redirects=False)

    assert response.status_code == 302
    db.session.refresh(exercise)
    db.session.refresh(q)
    assert exercise.version == 2
    assert q.question_text == 'Edited Q'
    assert q.correct_answer == 'C'

def test_create_writing_topic_success(client, teacher_user):
    login_as(client, teacher_user.email)

    response = client.post('/teacher/writing/create', data={
        'title': 'Describe your hometown',
        'level': 'A2',
        'min_words': 100,
        'max_words': 150,
        'description': 'Write about your hometown in 100-150 words.'
    }, follow_redirects=False)

    assert response.status_code == 302
    assert '/teacher/dashboard' in response.headers['Location']

    topic = WritingTopic.query.filter_by(title='Describe your hometown').first()
    assert topic is not None
    assert topic.status == 'published'
    assert topic.created_by == teacher_user.id
    assert topic.min_words == 100
    assert topic.max_words == 150


def test_edit_writing_topic_with_submission_bumps_version(client, teacher_user, init_database):
    login_as(client, teacher_user.email)
    topic = WritingTopic(
        title='Writing v1',
        description='Desc',
        level='B1',
        min_words=150,
        max_words=200,
        created_by=teacher_user.id,
        version=1
    )
    db.session.add(topic)
    db.session.commit()

    sub = Submission(
        user_id=init_database.id,
        exercise_id=topic.id,
        skill='writing',
        total_score=75.0
    )
    db.session.add(sub)
    db.session.commit()

    client.post(f'/teacher/writing/{topic.id}/edit', data={
        'title': 'Writing v2',
        'level': 'B2',
        'min_words': 180,
        'max_words': 250,
        'description': 'Updated Desc'
    }, follow_redirects=False)

    db.session.refresh(topic)
    assert topic.version == 2
    assert topic.title == 'Writing v2'
    assert topic.level == 'B2'


def test_delete_writing_hard_vs_soft(client, teacher_user, init_database):
    login_as(client, teacher_user.email)

    topic1 = WritingTopic(
        title='No Submission Topic',
        description='Desc 1',
        level='A1',
        created_by=teacher_user.id
    )
    db.session.add(topic1)
    db.session.commit()
    t1_id = topic1.id

    client.post(f'/teacher/writing/{t1_id}/delete', follow_redirects=False)
    assert WritingTopic.query.get(t1_id) is None

    topic2 = WritingTopic(
        title='Has Submission Topic',
        description='Desc 2',
        level='A1',
        created_by=teacher_user.id,
        is_active=True
    )
    db.session.add(topic2)
    db.session.commit()

    sub = Submission(
        user_id=init_database.id,
        exercise_id=topic2.id,
        skill='writing',
        total_score=60.0
    )
    db.session.add(sub)
    db.session.commit()

    client.post(f'/teacher/writing/{topic2.id}/delete', follow_redirects=False)
    db.session.refresh(topic2)
    assert topic2.is_active is False



# 5. CHẤM BÀI VIẾT (TEACHER GRADE & FEEDBACK)
def test_grade_writing_submission_updates_score_and_sends_notification(client, teacher_user, init_database):
    login_as(client, teacher_user.email)
    topic = WritingTopic(
        title='Essay on Environment',
        description='Write about environmental issues.',
        level='B2',
        created_by=teacher_user.id
    )
    db.session.add(topic)
    db.session.commit()

    submission = Submission(
        user_id=init_database.id,
        exercise_id=topic.id,
        skill='writing',
        content_submitted='This is my essay about green energy.',
        total_score=70.0,
        ai_feedback='Good vocabulary.'
    )
    db.session.add(submission)
    db.session.commit()

    response = client.post(f'/teacher/writing/submission/{submission.id}/grade', data={
        'teacher_score': 85.5,
        'teacher_feedback': 'Rất tốt, cần cải thiện mở bài một chút.'
    }, follow_redirects=False)

    assert response.status_code == 302
    assert f'/teacher/writing/{topic.id}/submissions' in response.headers['Location']

    db.session.refresh(submission)
    assert submission.total_score == 85.5
    assert '### 👨‍🏫 Nhận xét từ Giáo viên:' in submission.ai_feedback
    assert 'Rất tốt, cần cải thiện mở bài một chút.' in submission.ai_feedback
    assert 'Good vocabulary.' in submission.ai_feedback

    notification = Notification.query.filter_by(user_id=init_database.id).first()
    assert notification is not None
    assert 'Giáo viên đã nhận xét bài làm của bạn' in notification.title
    assert topic.title in notification.message


# ----------------------------------------------------------------------
# 6. CÁC TEST CASE KHÔNG HỢP LỆ (INVALID / EDGE / ERROR CASES)
# ----------------------------------------------------------------------

def test_manage_reading_questions_forbidden_for_other_teacher(client, teacher_user, other_teacher):
    exercise = ReadingExercise(
        title='Teacher1 Exercise',
        content='Passage content',
        level='A1',
        created_by=teacher_user.id
    )
    db.session.add(exercise)
    db.session.commit()

    login_as(client, other_teacher.email)
    response = client.get(f'/teacher/reading/{exercise.id}/questions', follow_redirects=False)
    assert response.status_code == 302
    assert '/teacher/dashboard' in response.headers['Location']


def test_delete_reading_question_forbidden_for_other_teacher(client, teacher_user, other_teacher):
    exercise = ReadingExercise(
        title='Teacher1 Exercise',
        content='Passage content',
        level='A1',
        created_by=teacher_user.id
    )
    db.session.add(exercise)
    db.session.commit()

    q = ReadingQuestion(
        exercise_id=exercise.id,
        question_text='Q1',
        option_a='1', option_b='2', option_c='3', option_d='4',
        correct_answer='A',
        level='A1'
    )
    db.session.add(q)
    db.session.commit()
    q_id = q.id

    login_as(client, other_teacher.email)
    response = client.post(f'/teacher/reading/{exercise.id}/questions/{q_id}/delete', follow_redirects=False)
    assert response.status_code == 302
    assert '/teacher/dashboard' in response.headers['Location']
    assert ReadingQuestion.query.get(q_id) is not None


def test_edit_reading_question_forbidden_for_other_teacher(client, teacher_user, other_teacher):
    exercise = ReadingExercise(
        title='Teacher1 Exercise',
        content='Passage content',
        level='A1',
        created_by=teacher_user.id
    )
    db.session.add(exercise)
    db.session.commit()

    q = ReadingQuestion(
        exercise_id=exercise.id,
        question_text='Original Q',
        option_a='1', option_b='2', option_c='3', option_d='4',
        correct_answer='A',
        level='A1'
    )
    db.session.add(q)
    db.session.commit()

    login_as(client, other_teacher.email)
    response = client.post(f'/teacher/reading/{exercise.id}/questions/{q.id}/edit', data={
        'content': 'Hacked Question Content',
        'option_a': 'A',
        'option_b': 'B',
        'option_c': 'C',
        'option_d': 'D',
        'correct_answer': 'B'
    }, follow_redirects=False)
    assert response.status_code == 302
    assert '/teacher/dashboard' in response.headers['Location']

    db.session.refresh(q)
    assert q.question_text == 'Original Q'


def test_writing_actions_forbidden_for_other_teacher(client, teacher_user, other_teacher):
    topic = WritingTopic(
        title='Teacher1 Topic',
        description='Topic Desc',
        level='A1',
        created_by=teacher_user.id
    )
    db.session.add(topic)
    db.session.commit()

    login_as(client, other_teacher.email)

    res_edit = client.post(f'/teacher/writing/{topic.id}/edit', data={
        'title': 'Hacked Topic',
        'level': 'A2',
        'min_words': 50,
        'max_words': 100,
        'description': 'Hacked'
    }, follow_redirects=False)
    assert res_edit.status_code == 302
    assert '/teacher/dashboard' in response_redirect_url(res_edit)
    db.session.refresh(topic)
    assert topic.title == 'Teacher1 Topic'

    res_delete = client.post(f'/teacher/writing/{topic.id}/delete', follow_redirects=False)
    assert res_delete.status_code == 302
    assert '/teacher/dashboard' in response_redirect_url(res_delete)
    assert WritingTopic.query.get(topic.id) is not None


def test_student_forbidden_from_all_writing_actions(client, teacher_user, init_database):
    topic = WritingTopic(
        title='Teacher Topic',
        description='Desc',
        level='A1',
        created_by=teacher_user.id
    )
    db.session.add(topic)
    db.session.commit()

    sub = Submission(
        user_id=init_database.id,
        exercise_id=topic.id,
        skill='writing',
        total_score=50.0
    )
    db.session.add(sub)
    db.session.commit()

    login_as(client, 'test@learneng.com', 'Tuan@123')

    res_create = client.post('/teacher/writing/create', data={
        'title': 'Student Writing',
        'description': 'Desc',
        'level': 'A1',
        'min_words': 50,
        'max_words': 100
    }, follow_redirects=False)
    assert res_create.status_code == 302

    res_view = client.get(f'/teacher/writing/{topic.id}/submissions', follow_redirects=False)
    assert res_view.status_code == 302

    res_grade = client.post(f'/teacher/writing/submission/{sub.id}/grade', data={
        'teacher_score': 100.0
    }, follow_redirects=False)
    assert res_grade.status_code == 302


def test_nonexistent_ids_return_404(client, teacher_user):
    login_as(client, teacher_user.email)
    NON_EXISTENT_ID = 99999

    assert client.get(f'/teacher/reading/{NON_EXISTENT_ID}/questions').status_code == 404
    assert client.get(f'/teacher/reading/{NON_EXISTENT_ID}/edit').status_code == 404
    assert client.post(f'/teacher/reading/{NON_EXISTENT_ID}/delete').status_code == 404
    assert client.get(f'/teacher/writing/{NON_EXISTENT_ID}/edit').status_code == 404
    assert client.post(f'/teacher/writing/{NON_EXISTENT_ID}/delete').status_code == 404
    assert client.get(f'/teacher/writing/{NON_EXISTENT_ID}/submissions').status_code == 404
    assert client.post(f'/teacher/writing/submission/{NON_EXISTENT_ID}/grade').status_code == 404


def test_grade_writing_submission_invalid_empty_score(client, teacher_user, init_database):
    login_as(client, teacher_user.email)
    topic = WritingTopic(
        title='Writing Test Empty Score',
        description='Write essay',
        level='B1',
        created_by=teacher_user.id
    )
    db.session.add(topic)
    db.session.commit()

    sub = Submission(
        user_id=init_database.id,
        exercise_id=topic.id,
        skill='writing',
        total_score=65.0,
        ai_feedback='Initial AI feedback'
    )
    db.session.add(sub)
    db.session.commit()

    response = client.post(f'/teacher/writing/submission/{sub.id}/grade', data={
        'teacher_score': '',
        'teacher_feedback': 'Some feedback'
    }, follow_redirects=False)

    assert response.status_code == 302
    db.session.refresh(sub)
    assert sub.total_score == 65.0
    assert sub.ai_feedback == 'Initial AI feedback'


def response_redirect_url(res):
    return res.headers.get('Location', '')

