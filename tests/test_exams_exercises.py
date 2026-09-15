import pytest
from extensions import db
from modules.users.models import User
from modules.exams.models import ReadingExercise, ReadingQuestion, Submission
from modules.exams.services import (
    calculate_placement_level,
    update_progress_points,
    grade_reading_submission
)
from utils.utils import Role

@pytest.mark.parametrize("score,expected_level", [
    (15, 'A1'),
    (20, 'A1'),
    (35, 'A2'),
    (40, 'A2'),
    (55, 'B1'),
    (60, 'B1'),
    (70, 'B2'),
    (75, 'B2'),
    (85, 'C1'),
    (90, 'C1'),
    (95, 'C2'),
    (100, 'C2'),
])
def test_calculate_placement_level(score, expected_level):
    assert calculate_placement_level(score) == expected_level


def test_update_progress_points_reading(app, init_database):
    user = User.query.filter_by(email="test@learneng.com").first()
    initial_pp = user.progress_points

    earned_1 = update_progress_points(user, 'reading', score=70)
    assert earned_1 == 5
    assert user.progress_points == initial_pp + 5

    earned_2 = update_progress_points(user, 'reading', score=90)
    assert earned_2 == 10
    assert user.progress_points == initial_pp + 15



@pytest.fixture
def sample_reading_exercise(app, init_database):
    exercise = ReadingExercise(
        title="Test Reading",
        content="Sample content for testing.",
        level="A1",
        created_by=init_database.id,
        status="published"
    )
    db.session.add(exercise)
    db.session.commit()

    q1 = ReadingQuestion(
        exercise_id=exercise.id,
        question_text="Question 1?",
        option_a="Apple", option_b="Banana", option_c="Orange", option_d="Grape",
        correct_answer="A",
        level="A1"
    )
    q2 = ReadingQuestion(
        exercise_id=exercise.id,
        question_text="Question 2?",
        option_a="Dog", option_b="Cat", option_c="Bird", option_d="Fish",
        correct_answer="B",
        level="A1"
    )
    db.session.add_all([q1, q2])
    db.session.commit()
    return exercise


def test_grade_reading_deducts_heart_when_wrong(app, init_database, sample_reading_exercise):
    user = User.query.filter_by(email="test@learneng.com").first()
    user.hearts_count = 5
    user.is_premium = False
    db.session.commit()

    questions = sample_reading_exercise.questions
    form_data = {
        f'q_{questions[0].id}': 'A',
        f'q_{questions[1].id}': 'C'
    }

    sub_id, score, wrong, pp, hearts_deducted = grade_reading_submission(
        user, sample_reading_exercise.id, form_data
    )

    assert score == 50.0
    assert wrong == 1
    assert hearts_deducted == 1
    assert user.hearts_count == 4


def test_grade_reading_redo_perfect_score_rewards_heart(app, init_database, sample_reading_exercise):
    user = User.query.filter_by(email="test@learneng.com").first()
    user.hearts_count = 3
    user.is_premium = False

    old_sub = Submission(
        user_id=user.id,
        exercise_id=sample_reading_exercise.id,
        skill='reading',
        total_score=50.0
    )
    db.session.add(old_sub)
    db.session.commit()

    questions = sample_reading_exercise.questions
    form_data = {
        f'q_{questions[0].id}': 'A',
        f'q_{questions[1].id}': 'B'
    }

    sub_id, score, wrong, pp, hearts_deducted = grade_reading_submission(
        user, sample_reading_exercise.id, form_data
    )

    assert score == 100.0
    assert wrong == 0
    assert user.hearts_count == 4


def test_grade_reading_premium_never_loses_heart(app, init_database, sample_reading_exercise):
    user = User.query.filter_by(email="test@learneng.com").first()
    user.hearts_count = 5
    user.is_premium = True
    db.session.commit()

    questions = sample_reading_exercise.questions
    form_data = {
        f'q_{questions[0].id}': 'D',
        f'q_{questions[1].id}': 'D'
    }

    sub_id, score, wrong, pp, hearts_deducted = grade_reading_submission(
        user, sample_reading_exercise.id, form_data
    )

    assert wrong == 2
    assert hearts_deducted == 0
    assert user.hearts_count == 5



def test_update_progress_points_writing(app, init_database):
    user = User.query.filter_by(email="test@learneng.com").first()
    initial_pp = user.progress_points

    earned_low = update_progress_points(user, 'writing', score=60)
    assert earned_low == 10
    assert user.progress_points == initial_pp + 10

    earned_high = update_progress_points(user, 'writing', score=80)
    assert earned_high == 20
    assert user.progress_points == initial_pp + 30


def test_grade_reading_redo_not_perfect_still_deducts_heart(app, init_database, sample_reading_exercise):
    user = User.query.filter_by(email="test@learneng.com").first()
    user.hearts_count = 5
    user.is_premium = False

    old_sub = Submission(
        user_id=user.id,
        exercise_id=sample_reading_exercise.id,
        skill='reading',
        total_score=100.0
    )
    db.session.add(old_sub)
    db.session.commit()

    questions = sample_reading_exercise.questions
    form_data = {
        f'q_{questions[0].id}': 'A',
        f'q_{questions[1].id}': 'D'
    }

    sub_id, score, wrong, pp, hearts_deducted = grade_reading_submission(
        user, sample_reading_exercise.id, form_data
    )

    assert score == 50.0
    assert wrong == 1
    assert hearts_deducted == 1
    assert user.hearts_count == 4


def test_grade_reading_hearts_floor_at_zero(app, init_database, sample_reading_exercise):
    user = User.query.filter_by(email="test@learneng.com").first()
    user.hearts_count = 0
    user.is_premium = False
    db.session.commit()

    questions = sample_reading_exercise.questions
    form_data = {
        f'q_{questions[0].id}': 'D',
        f'q_{questions[1].id}': 'D'
    }

    sub_id, score, wrong, pp, hearts_deducted = grade_reading_submission(
        user, sample_reading_exercise.id, form_data
    )

    assert wrong == 2
    assert user.hearts_count == 0

from unittest.mock import patch, MagicMock
from modules.exams.services import (
    get_reading_explanation_from_ai,
    grade_writing_with_ai,
    generate_placement_test
)
from modules.exams.models import WritingTopic


def test_grade_reading_zero_questions(app, init_database):
    user = User.query.filter_by(email="test@learneng.com").first()
    empty_exercise = ReadingExercise(
        title="Empty Questions Reading",
        content="Passage without questions",
        level="A1",
        created_by=user.id
    )
    db.session.add(empty_exercise)
    db.session.commit()

    sub_id, final_score, wrong_count, pp_earned, hearts_deducted = grade_reading_submission(
        user, empty_exercise.id, {}
    )

    assert sub_id == 0
    assert final_score == 0
    assert wrong_count == 0
    assert pp_earned == 0
    assert hearts_deducted == 0


def test_grade_reading_empty_form_data_all_wrong(app, init_database, sample_reading_exercise):
    user = User.query.filter_by(email="test@learneng.com").first()
    user.hearts_count = 5
    user.is_premium = False
    db.session.commit()

    sub_id, score, wrong, pp, hearts_deducted = grade_reading_submission(
        user, sample_reading_exercise.id, {}
    )

    assert score == 0.0
    assert wrong == 2
    assert hearts_deducted == 2
    assert user.hearts_count == 3


def test_update_progress_points_unknown_skill(app, init_database):
    user = User.query.filter_by(email="test@learneng.com").first()
    initial_pp = user.progress_points

    earned = update_progress_points(user, 'listening', score=90)
    assert earned == 0
    assert user.progress_points == initial_pp


def test_get_reading_explanation_from_ai_nonexistent_submission(app, init_database):
    result = get_reading_explanation_from_ai(99999)
    assert result == "Không tìm thấy bài nộp."


def test_get_reading_explanation_from_ai_handles_exception(app, init_database, sample_reading_exercise):
    user = User.query.filter_by(email="test@learneng.com").first()
    sub = Submission(
        user_id=user.id,
        exercise_id=sample_reading_exercise.id,
        skill='reading',
        total_score=50.0
    )
    db.session.add(sub)
    db.session.commit()

    with patch('modules.exams.services.genai.Client', side_effect=Exception('AI connection timed out')):
        result = get_reading_explanation_from_ai(sub.id)
        assert "Lỗi khi gọi Trợ giảng AI" in result
        assert "AI connection timed out" in result


def test_grade_writing_with_ai_handles_exception(app, init_database):
    topic = WritingTopic(
        title="Test Topic",
        description="Describe climate change",
        level="B1",
        created_by=init_database.id
    )
    db.session.add(topic)
    db.session.commit()

    with patch('modules.exams.services.genai.Client', side_effect=Exception('Quota exceeded')):
        result = grade_writing_with_ai(topic, "My essay about climate change.")
        assert result is None


def test_grade_writing_with_ai_invalid_json_response(app, init_database):
    topic = WritingTopic(
        title="Test Topic 2",
        description="Describe pollution",
        level="A2",
        created_by=init_database.id
    )
    db.session.add(topic)
    db.session.commit()

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Xin chào, đây là bài viết rất hay nhưng tôi không trả về JSON."
    mock_client.models.generate_content.return_value = mock_response

    with patch('modules.exams.services.genai.Client', return_value=mock_client):
        result = grade_writing_with_ai(topic, "Essay content")
        assert result is None


def test_generate_placement_test_fallback_when_few_questions(app, init_database):
    q1 = ReadingQuestion(
        question_text="C2 Q1",
        option_a="A", option_b="B", option_c="C", option_d="D",
        correct_answer="A", level="C2", is_placement_test=True
    )
    q2 = ReadingQuestion(
        question_text="C2 Q2",
        option_a="A", option_b="B", option_c="C", option_d="D",
        correct_answer="B", level="C2", is_placement_test=True
    )
    db.session.add_all([q1, q2])
    db.session.commit()

    questions = generate_placement_test()
    c2_questions = [q for q in questions if q.level == 'C2']
    assert len(c2_questions) == 2
