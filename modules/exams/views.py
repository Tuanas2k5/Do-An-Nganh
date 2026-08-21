from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from modules.exams.services import (generate_placement_test, calculate_placement_level, grade_reading_submission,
                                    get_reading_explanation_from_ai, grade_writing_with_ai)
from extensions import db
from modules.exams.models import ReadingQuestion, ReadingExercise, Submission, WritingTopic
from datetime import datetime, timedelta

exams_bp = Blueprint('exams', __name__, url_prefix='/exams')

@exams_bp.route('/placement-test', methods=['GET', 'POST'])
@login_required
def placement_test_page():
    if current_user.has_done_placement:
        flash('Bạn đã hoàn thành bài kiểm tra đầu vào rồi!', 'warning')
        return redirect(url_for('index'))

    if request.method == 'POST':
        action = request.form.get('action')


        if action == 'skip':
            current_user.current_level = 'A1'
            current_user.has_done_placement = True
            db.session.commit()

            flash('Bạn đã bỏ qua bài kiểm tra đầu vào. Cấp độ hiện tại của bạn là A1.', 'info')
            return redirect(url_for('index'))

        elif action == 'submit':
            placement_questions = ReadingQuestion.query.filter_by(is_placement_test=True).all()
            total_questions = len(placement_questions)
            correct_answers = 0

            if total_questions == 0:
                flash('Hệ thống chưa có đề thi, vui lòng thử lại sau!', 'danger')
                return redirect(url_for('index'))

            for question in placement_questions:
                user_answer = request.form.get(f'q_{question.id}')
                if user_answer == question.correct_answer:
                    correct_answers += 1

            score_percentage = (correct_answers / total_questions) * 100
            assigned_level = calculate_placement_level(score_percentage)

            current_user.current_level = assigned_level
            current_user.has_done_placement = True
            db.session.commit()

            flash(f'Chúc mừng! Bạn đạt {score_percentage}%. Cấp độ của bạn được xếp vào {assigned_level}.', 'success')
            return redirect(url_for('index'))

    questions = generate_placement_test()
    return render_template('placement_test.html', questions=questions)


CEFR_LEVELS = {'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5, 'C2': 6}

@exams_bp.route('/reading/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def reading_exercise_page(exercise_id):
    exercise = ReadingExercise.query.get_or_404(exercise_id)

    user_lvl_val = CEFR_LEVELS.get(current_user.current_level, 1)
    exercise_lvl_val = CEFR_LEVELS.get(exercise.level, 1)

    if exercise_lvl_val > user_lvl_val:
        flash(f'Bài tập này yêu cầu cấp độ {exercise.level}. Bạn cần nâng cấp độ để tham gia!', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        if not current_user.is_premium and current_user.hearts_count <= 0:
            flash('Bạn đã hết Tim! Vui lòng chờ hồi phục hoặc nâng cấp PREMIUM để tiếp tục.', 'danger')
            return redirect(url_for('index'))

        submission_id, final_score, wrong_count, pp_earned, hearts_deducted = grade_reading_submission(
            current_user,
            exercise_id,
            request.form
        )

        flash('Nộp bài thành công!', 'success')
        return redirect(url_for('exams.reading_result_page', submission_id=submission_id))

    return render_template('reading_exercise.html', exercise=exercise)

@exams_bp.route('/reading/result/<int:submission_id>')
@login_required
def reading_result_page(submission_id):
    submission = Submission.query.get_or_404(submission_id)

    if submission.user_id != current_user.id:
        flash('Bạn không có quyền xem kết quả này.', 'danger')
        return redirect(url_for('index'))

    exercise = ReadingExercise.query.get(submission.exercise_id)

    return render_template('reading_result.html', submission=submission, exercise=exercise)


@exams_bp.before_app_request
def auto_recover_hearts():
    if current_user.is_authenticated and not current_user.is_premium:
        MAX_HEARTS = 5

        if current_user.hearts_count < MAX_HEARTS:
            now = datetime.now()
            last_update = current_user.last_heart_update or now

            diff = now - last_update
            minutes_passed = diff.total_seconds() / 60

            hearts_to_add = int(minutes_passed // 10)

            if hearts_to_add > 0:
                current_user.hearts_count = min(MAX_HEARTS, current_user.hearts_count + hearts_to_add)
                current_user.last_heart_update = last_update + timedelta(minutes=hearts_to_add * 10)

                db.session.commit()


@exams_bp.route('/api/reading/explain/<int:submission_id>', methods=['GET'])
@login_required
def api_explain_reading(submission_id):
    submission = Submission.query.get_or_404(submission_id)

    # Bảo mật: Chỉ chủ nhân bài làm mới được xem giải thích
    if submission.user_id != current_user.id:
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    explanation_text = get_reading_explanation_from_ai(submission_id)

    submission.ai_feedback = explanation_text
    db.session.commit()

    return jsonify({
        "status": "success",
        "data": explanation_text
    })

@exams_bp.route('/writing/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def writing_exercise_page(exercise_id):
    exercise = WritingTopic.query.get_or_404(exercise_id)

    user_lvl_val = CEFR_LEVELS.get(current_user.current_level, 1)
    exercise_lvl_val = CEFR_LEVELS.get(exercise.level, 1)

    if exercise_lvl_val > user_lvl_val:
        flash(f'Bài tập này yêu cầu cấp độ {exercise.level}. Bạn cần nâng cấp độ để tham gia!', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        if not current_user.is_premium and current_user.hearts_count < 2:
            flash('Bạn cần ít nhất 2 Tim để nộp bài Writing!', 'danger')
            return redirect(url_for('index'))

        student_essay = request.form.get('student_essay')

        ai_result = grade_writing_with_ai(exercise, student_essay)

        if not ai_result:
            flash('Hệ thống AI đang quá tải, vui lòng nộp lại sau!', 'danger')
            return redirect(request.url)

        new_submission = Submission(
            user_id=current_user.id,
            exercise_id=exercise.id,
            skill='writing',
            content_submitted=student_essay,

            total_score=ai_result.get('total_score', 0),
            grammar_score=ai_result.get('grammar_score', 0),
            vocabulary_score=ai_result.get('vocabulary_score', 0),
            coherence_score=ai_result.get('coherence_score', 0),
            task_response_score=ai_result.get('task_response_score', 0),

            ai_feedback=ai_result.get('ai_feedback', '')
        )
        db.session.add(new_submission)

        if not current_user.is_premium:
            current_user.hearts_count -= 2

        pp_earned = 10 if new_submission.total_score >= 50 else 5
        current_user.progress_points += pp_earned

        db.session.commit()

        flash('Nộp bài và chấm điểm thành công!', 'success')
        return redirect(url_for('exams.writing_result_page', submission_id=new_submission.id))

    return render_template('writing_exercise.html', exercise=exercise)


@exams_bp.route('/writing/result/<int:submission_id>')
@login_required
def writing_result_page(submission_id):
    submission = Submission.query.get_or_404(submission_id)

    if submission.user_id != current_user.id or submission.skill != 'writing':
        flash('Bạn không có quyền xem kết quả này!', 'danger')
        return redirect(url_for('index'))

    topic = WritingTopic.query.get(submission.exercise_id)

    return render_template('writing_result.html', submission=submission, topic=topic)