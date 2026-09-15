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
    return render_template('student/placement_test.html', questions=questions)

@exams_bp.route('/level-up', methods=['GET', 'POST'])
@login_required
def level_up_exam():
    thresholds = {'A1': 100, 'A2': 150, 'B1': 200, 'B2': 250, 'C1': 300, 'C2': float('inf')}
    current_threshold = thresholds.get(current_user.current_level, 100)

    if current_user.progress_points < current_threshold:
        flash('Bạn chưa tích đủ Điểm Tiến độ (PP) để thi lên cấp!', 'warning')
        return redirect(url_for('index'))

    if not current_user.is_premium and current_user.hearts_count < 3:
        flash('Bạn cần ít nhất 3 Tim để làm bài thi này. Hãy chờ hồi phục hoặc nâng cấp Premium!', 'danger')
        return redirect(url_for('index'))

    reading_qs = ReadingQuestion.query.filter_by(level=current_user.current_level, is_placement_test=False).order_by(db.func.random()).limit(10).all()
    writing_topic = WritingTopic.query.filter_by(level=current_user.current_level).order_by(db.func.random()).first()

    if not reading_qs or not writing_topic:
        flash('Hệ thống chưa đủ ngân hàng đề thi cho cấp độ này. Vui lòng quay lại sau!', 'info')
        return redirect(url_for('index'))

    if request.method == 'POST':
        if not current_user.is_premium:
            current_user.hearts_count = max(0, current_user.hearts_count - 3)

        correct_answers = 0
        for q in reading_qs:
            user_ans = request.form.get(f'q_{q.id}')
            if user_ans == q.correct_answer:
                correct_answers += 1

        reading_score = correct_answers * 10

        student_essay = request.form.get('student_essay')

        ai_result = grade_writing_with_ai(writing_topic, student_essay)
        if not ai_result:
            db.session.commit()
            flash('Hệ thống chấm điểm AI đang quá tải, vui lòng nộp lại sau!', 'danger')
            return redirect(request.url)

        writing_score = ai_result.get('total_score', 0)

        final_score = (reading_score * 0.5) + (writing_score * 0.5)

        CEFR_ORDER = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        current_index = CEFR_ORDER.index(current_user.current_level)

        if final_score >= 70:
            if current_index < len(CEFR_ORDER) - 1:
                current_user.current_level = CEFR_ORDER[current_index + 1]

            current_user.progress_points = 0
            flash(
                f'XUẤT SẮC! Bạn đạt {final_score}/100 điểm. Chúc mừng bạn đã thăng cấp lên {current_user.current_level}!',
                'success')

        else:
            penalty = int(current_threshold * 0.5)
            current_user.progress_points = max(0, current_user.progress_points - penalty)
            flash(
                f'Rất tiếc! Bạn chỉ đạt {final_score}/100 điểm (Yêu cầu: 70). Hệ thống đã trừ {penalty} PP, hãy ôn luyện thêm nhé!',
                'danger')

        reading_sub = Submission(
            user_id=current_user.id,
            skill='level_up_reading',
            total_score=reading_score
        )
        db.session.add(reading_sub)

        writing_sub = Submission(
            user_id=current_user.id,
            exercise_id=writing_topic.id,
            skill='level_up_writing',
            content_submitted=student_essay,
            total_score=writing_score,
            grammar_score=ai_result.get('grammar_score', 0),
            vocabulary_score=ai_result.get('vocabulary_score', 0),
            coherence_score=ai_result.get('coherence_score', 0),
            task_response_score=ai_result.get('task_response_score', 0),
            ai_feedback=ai_result.get('ai_feedback', '')
        )
        db.session.add(writing_sub)

        db.session.commit()

        is_passed = final_score >= 70
        return render_template('student/level_up_result.html',
                               final_score=final_score,
                               reading_score=reading_score,
                               writing_score=writing_score,
                               is_passed=is_passed,
                               penalty=penalty if not is_passed else 0)

    return render_template('student/level_up_test.html', reading_qs=reading_qs, writing_topic=writing_topic)


CEFR_LEVELS = {'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5, 'C2': 6}

@exams_bp.route('/reading/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def reading_exercise_page(exercise_id):
    exercise = ReadingExercise.query.get_or_404(exercise_id)

    user_lvl_val = CEFR_LEVELS.get(current_user.current_level, 1)
    exercise_lvl_val = CEFR_LEVELS.get(exercise.level, 1)

    if exercise_lvl_val > user_lvl_val and not current_user.is_premium:
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
        return redirect(url_for('exams.reading_result_page', submission_id=submission_id, pp=pp_earned, hearts=hearts_deducted))

    return render_template('reading/reading_exercise.html', exercise=exercise)

@exams_bp.route('/reading/result/<int:submission_id>')
@login_required
def reading_result_page(submission_id):
    submission = Submission.query.get_or_404(submission_id)

    if submission.user_id != current_user.id:
        flash('Bạn không có quyền xem kết quả này.', 'danger')
        return redirect(url_for('index'))

    exercise = ReadingExercise.query.get(submission.exercise_id)
    pp_earned = request.args.get('pp', 0)
    hearts_deducted = request.args.get('hearts', 0)

    return render_template('reading/reading_result.html', submission=submission, exercise=exercise, pp_earned=pp_earned,
                           hearts_deducted=hearts_deducted)


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

    if exercise_lvl_val > user_lvl_val and not current_user.is_premium:
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

    return render_template('writing/writing_exercise.html', exercise=exercise)


@exams_bp.route('/writing/result/<int:submission_id>')
@login_required
def writing_result_page(submission_id):
    submission = Submission.query.get_or_404(submission_id)

    if submission.user_id != current_user.id or submission.skill != 'writing':
        flash('Bạn không có quyền xem kết quả này!', 'danger')
        return redirect(url_for('index'))

    topic = WritingTopic.query.get(submission.exercise_id)

    return render_template('writing/writing_result.html', submission=submission, topic=topic)