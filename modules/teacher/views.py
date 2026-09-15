from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from modules.exams.models import ReadingExercise, ReadingQuestion, Submission, WritingTopic
from extensions import db
from modules.users.models import User, Notification
from utils.utils import Role

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')

@teacher_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role.value not in ['teacher', 'admin']:
        return "Bạn không có quyền truy cập trang này", 403

    my_readings = ReadingExercise.query.filter_by(
        created_by=current_user.id,
        is_active=True
    ).order_by(ReadingExercise.id.desc()).all()

    my_writings = WritingTopic.query.filter_by(
        created_by=current_user.id,
        is_active=True
    ).order_by(WritingTopic.id.desc()).all()

    students = User.query.filter_by(role=Role.STUDENT).order_by(User.progress_points.desc()).all()

    return render_template('teacher/dashboard.html', readings=my_readings, writings=my_writings, students=students)

@teacher_bp.route('/reading/create', methods=['GET', 'POST'])
@login_required
def create_reading():
    if current_user.role.value not in ['teacher', 'admin']:
        flash('Bạn không có quyền thực hiện chức năng này!', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form.get('title')
        level = request.form.get('level')
        time_limit = request.form.get('time_limit', type=int)
        content = request.form.get('content')

        new_exercise = ReadingExercise(
            title=title,
            level=level,
            time_limit=time_limit,
            content=content,
            created_by=current_user.id,
            status='draft',
            is_active=True,
            version=1
        )
        db.session.add(new_exercise)
        db.session.commit()

        flash('Tạo bài đọc nháp thành công! Hãy thêm câu hỏi để phát hành.', 'success')
        return redirect(url_for('teacher.dashboard'))

    return render_template('teacher/create_reading.html')


@teacher_bp.route('/reading/<int:exercise_id>/questions', methods=['GET', 'POST'])
@login_required
def manage_reading_questions(exercise_id):
    if current_user.role.value not in ['teacher', 'admin']:
        flash('Bạn không có quyền truy cập!', 'danger')
        return redirect(url_for('index'))

    exercise = ReadingExercise.query.get_or_404(exercise_id)

    if exercise.created_by != current_user.id:
        flash('Bạn không có quyền chỉnh sửa bài tập của giáo viên khác!', 'danger')
        return redirect(url_for('teacher.dashboard'))

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'publish':
            if len(exercise.questions) >= 5:
                exercise.status = 'published'
                db.session.commit()
                flash('Phát hành đề thi thành công! Học sinh đã có thể làm bài.', 'success')
                return redirect(url_for('teacher.dashboard'))
            else:
                flash('Cần tối thiểu 5 câu hỏi để phát hành!', 'danger')
                return redirect(url_for('teacher.manage_reading_questions', exercise_id=exercise.id))

        elif action == 'add_question':
            content = request.form.get('content')
            option_a = request.form.get('option_a')
            option_b = request.form.get('option_b')
            option_c = request.form.get('option_c')
            option_d = request.form.get('option_d')
            correct_answer = request.form.get('correct_answer')

            new_question = ReadingQuestion(
                exercise_id=exercise.id,
                question_text=content,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_answer=correct_answer,
                level=exercise.level
            )
            db.session.add(new_question)
            db.session.commit()

            flash('Đã thêm câu hỏi thành công!', 'success')
            return redirect(url_for('teacher.manage_reading_questions', exercise_id=exercise.id))

    # Lấy danh sách câu hỏi hiện tại
    questions = ReadingQuestion.query.filter_by(exercise_id=exercise.id).all()

    return render_template('teacher/manage_questions.html', exercise=exercise, questions=questions)

@teacher_bp.route('/reading/<int:exercise_id>/questions/<int:question_id>/delete', methods=['POST'])
@login_required
def delete_reading_question(exercise_id, question_id):
    if current_user.role.value not in ['teacher', 'admin']:
        flash('Bạn không có quyền thực hiện hành động này!', 'danger')
        return redirect(url_for('index'))

    exercise = ReadingExercise.query.get_or_404(exercise_id)

    if exercise.created_by != current_user.id:
        flash('Bạn không có quyền chỉnh sửa bài tập của người khác!', 'danger')
        return redirect(url_for('teacher.dashboard'))

    question = ReadingQuestion.query.get_or_404(question_id)

    db.session.delete(question)

    if exercise.status == 'published':
        exercise.status = 'draft'
        flash('Đã xóa câu hỏi. Đề thi được chuyển về Bản Nháp vì cấu trúc đã thay đổi!', 'warning')
    else:
        flash('Đã xóa câu hỏi thành công!', 'success')

    db.session.commit()

    return redirect(url_for('teacher.manage_reading_questions', exercise_id=exercise.id))


@teacher_bp.route('/reading/<int:exercise_id>/delete', methods=['POST'])
@login_required
def delete_reading(exercise_id):
    if current_user.role.value not in ['teacher', 'admin']:
        flash('Bạn không có quyền thực hiện hành động này!', 'danger')
        return redirect(url_for('index'))

    exercise = ReadingExercise.query.get_or_404(exercise_id)

    if exercise.created_by != current_user.id:
        flash('Bạn không có quyền xóa bài tập của giáo viên khác!', 'danger')
        return redirect(url_for('teacher.dashboard'))

    has_submissions = Submission.query.filter_by(exercise_id=exercise.id, skill='reading').first()

    if has_submissions:
        exercise.is_active = False
        flash(
            'Bài tập này đã có học sinh làm. Hệ thống đã chuyển sang trạng thái Ẩn thay vì xóa vĩnh viễn để giữ lại lịch sử điểm số!',
            'warning')
    else:
        db.session.delete(exercise)
        flash('Đã xóa bài tập thành công!', 'success')

    db.session.commit()

    return redirect(url_for('teacher.dashboard'))


@teacher_bp.route('/reading/<int:exercise_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_reading(exercise_id):
    if current_user.role.value not in ['teacher', 'admin']:
        flash('Bạn không có quyền thực hiện hành động này!', 'danger')
        return redirect(url_for('index'))

    exercise = ReadingExercise.query.get_or_404(exercise_id)

    if exercise.created_by != current_user.id:
        flash('Bạn không có quyền sửa bài tập của giáo viên khác!', 'danger')
        return redirect(url_for('teacher.dashboard'))

    if request.method == 'POST':
        exercise.title = request.form.get('title')
        exercise.level = request.form.get('level')
        exercise.time_limit = request.form.get('time_limit', type=int)
        exercise.content = request.form.get('content')

        has_submissions = Submission.query.filter_by(exercise_id=exercise.id, skill='reading').first()
        if has_submissions:
            exercise.version += 1
            flash(
                f'Đã cập nhật bài đọc! Do bài đã có học sinh làm nên hệ thống tự động lưu thành Phiên bản {exercise.version}.',
                'info')
        else:
            flash('Cập nhật thông tin bài đọc thành công!', 'success')

        db.session.commit()
        return redirect(url_for('teacher.dashboard'))

    return render_template('teacher/edit_reading.html', exercise=exercise)

@teacher_bp.route('/reading/<int:exercise_id>/questions/<int:question_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_reading_question(exercise_id, question_id):
    if current_user.role.value not in ['teacher', 'admin']:
        flash('Bạn không có quyền!', 'danger')
        return redirect(url_for('index'))

    exercise = ReadingExercise.query.get_or_404(exercise_id)
    if exercise.created_by != current_user.id:
        flash('Không có quyền!', 'danger')
        return redirect(url_for('teacher.dashboard'))

    question = ReadingQuestion.query.get_or_404(question_id)

    if request.method == 'POST':
        question.question_text = request.form.get('content')
        question.option_a = request.form.get('option_a')
        question.option_b = request.form.get('option_b')
        question.option_c = request.form.get('option_c')
        question.option_d = request.form.get('option_d')
        question.correct_answer = request.form.get('correct_answer')

        has_submissions = Submission.query.filter_by(exercise_id=exercise.id, skill='reading').first()
        if has_submissions:
            exercise.version += 1
            flash(f'Đã sửa câu hỏi! Cấu trúc đề thay đổi nên được nâng lên Phiên bản {exercise.version}.', 'info')
        else:
            flash('Cập nhật câu hỏi thành công!', 'success')

        db.session.commit()
        return redirect(url_for('teacher.manage_reading_questions', exercise_id=exercise.id))

    return render_template('teacher/edit_question.html', exercise=exercise, question=question)

@teacher_bp.route('/writing/create', methods=['GET', 'POST'])
@login_required
def create_writing():
    if current_user.role.value not in ['teacher', 'admin']:
        flash('Bạn không có quyền thực hiện chức năng này!', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form.get('title')
        level = request.form.get('level')
        min_words = request.form.get('min_words', type=int)
        max_words = request.form.get('max_words', type=int)
        description = request.form.get('description')

        new_topic = WritingTopic(
            title=title,
            description=description,
            level=level,
            min_words=min_words,
            max_words=max_words,
            created_by=current_user.id,
            status='published',
            is_active=True
        )
        db.session.add(new_topic)
        db.session.commit()

        flash('Đã tạo và phát hành đề Writing thành công!', 'success')
        return redirect(url_for('teacher.dashboard'))

    return render_template('teacher/create_writing.html')

@teacher_bp.route('/writing/<int:writing_id>/delete', methods=['POST'])
@login_required
def delete_writing(writing_id):
    if current_user.role.value not in ['teacher', 'admin']:
        flash('Bạn không có quyền thực hiện hành động này!', 'danger')
        return redirect(url_for('index'))

    writing = WritingTopic.query.get_or_404(writing_id)

    if writing.created_by != current_user.id:
        flash('Bạn không có quyền xóa bài tập của giáo viên khác!', 'danger')
        return redirect(url_for('teacher.dashboard'))

    has_submissions = Submission.query.filter_by(exercise_id=writing.id, skill='writing').first()

    if has_submissions:
        writing.is_active = False
        flash('Bài Writing đã có học sinh làm. Đã chuyển sang trạng thái Ẩn!', 'warning')
    else:
        # Xóa cứng
        db.session.delete(writing)
        flash('Đã xóa bài Writing thành công!', 'success')

    db.session.commit()
    return redirect(url_for('teacher.dashboard'))


@teacher_bp.route('/writing/<int:writing_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_writing(writing_id):
    if current_user.role.value not in ['teacher', 'admin']:
        flash('Bạn không có quyền thực hiện hành động này!', 'danger')
        return redirect(url_for('index'))

    writing = WritingTopic.query.get_or_404(writing_id)

    if writing.created_by != current_user.id:
        flash('Bạn không có quyền sửa bài tập của giáo viên khác!', 'danger')
        return redirect(url_for('teacher.dashboard'))

    if request.method == 'POST':
        writing.title = request.form.get('title')
        writing.level = request.form.get('level')
        writing.min_words = request.form.get('min_words', type=int)
        writing.max_words = request.form.get('max_words', type=int)
        writing.description = request.form.get('description')

        # BR 8.3: Nếu đã có người nộp bài, lưu phiên bản mới
        has_submissions = Submission.query.filter_by(exercise_id=writing.id, skill='writing').first()
        if has_submissions:
            writing.version += 1
            flash(f'Đã cập nhật! Vì bài đã có người làm nên hệ thống tự động lưu thành Phiên bản {writing.version}.',
                  'info')
        else:
            flash('Cập nhật đề Writing thành công!', 'success')

        db.session.commit()
        return redirect(url_for('teacher.dashboard'))

    return render_template('teacher/edit_writing.html', writing=writing)

@teacher_bp.route('/writing/<int:writing_id>/submissions', methods=['GET'])
@login_required
def view_writing_submissions(writing_id):
    if current_user.role.value not in ['teacher', 'admin']:
        flash('Bạn không có quyền truy cập!', 'danger')
        return redirect(url_for('index'))

    topic = WritingTopic.query.get_or_404(writing_id)
    # Lấy toàn bộ bài nộp của học sinh cho đề này
    submissions = Submission.query.filter_by(exercise_id=writing_id, skill='writing').order_by(Submission.id.desc()).all()

    return render_template('teacher/writing_submissions.html', topic=topic, submissions=submissions)


@teacher_bp.route('/writing/submission/<int:submission_id>/grade', methods=['POST'])
@login_required
def grade_writing_submission(submission_id):
    if current_user.role.value not in ['teacher', 'admin']:
        flash('Bạn không có quyền!', 'danger')
        return redirect(url_for('index'))

    submission = Submission.query.get_or_404(submission_id)

    new_score = request.form.get('teacher_score', type=float)
    teacher_feedback = request.form.get('teacher_feedback')

    if new_score is not None:
        submission.total_score = new_score

        if teacher_feedback:
            submission.ai_feedback = f"### 👨‍🏫 Nhận xét từ Giáo viên:\n{teacher_feedback}\n\n---\n\n{submission.ai_feedback}"

        topic = WritingTopic.query.get(submission.exercise_id)
        new_notification = Notification(
            user_id=submission.user_id,
            title="Giáo viên đã nhận xét bài làm của bạn",
            message=f"Đề bài: {topic.title}",
            link=url_for('exams.writing_result_page', submission_id=submission.id)
        )
        db.session.add(new_notification)

        db.session.commit()
        flash('Đã cập nhật điểm và nhận xét thành công!', 'success')

    return redirect(url_for('teacher.view_writing_submissions', writing_id=submission.exercise_id))