import random, os, json
from modules.exams.models import ReadingQuestion, ReadingExercise, Submission, StudentReadingAnswer
from extensions import db
from google import genai


def generate_placement_test():
    levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
    test_questions = []

    for level in levels:
        questions = ReadingQuestion.query.filter_by(level=level, is_placement_test=True).all()

        if len(questions) >= 5:
            test_questions.extend(random.sample(questions, 5))
        else:
            test_questions.extend(questions)

    return test_questions


def calculate_placement_level(score_percentage):
    if score_percentage <= 20:
        return 'A1'
    elif score_percentage <= 40:
        return 'A2'
    elif score_percentage <= 60:
        return 'B1'
    elif score_percentage <= 75:
        return 'B2'
    elif score_percentage <= 90:
        return 'C1'
    else:
        return 'C2'


def grade_reading_submission(user, exercise_id, form_data):
    exercise = ReadingExercise.query.get(exercise_id)
    questions = exercise.questions
    total_questions = len(questions)

    if total_questions == 0:
        return 0, 0, 0, 0

    new_submission = Submission(
        user_id=user.id,
        exercise_id=exercise.id,
        skill='reading',
        total_score=0
    )
    db.session.add(new_submission)
    db.session.flush()

    points_per_question = 100.0 / total_questions
    correct_count = 0
    wrong_count = 0

    for q in questions:
        user_answer = form_data.get(f'q_{q.id}')
        is_correct = (user_answer == q.correct_answer)

        if is_correct:
            correct_count += 1
        else:
            wrong_count += 1

        chi_tiet_dap_an = StudentReadingAnswer(
            submission_id=new_submission.id,
            question_id=q.id,
            selected_option=user_answer,
            is_correct=is_correct
        )
        db.session.add(chi_tiet_dap_an)

    final_score = round(correct_count * points_per_question, 2)
    new_submission.total_score = final_score

    pp_earned = 5
    if final_score >= 80: pp_earned += 5
    user.progress_points += pp_earned

    hearts_deducted = 0
    if not user.is_premium:
        hearts_deducted = wrong_count
        user.hearts_count = max(0, user.hearts_count - hearts_deducted)

    db.session.commit()
    return new_submission.id, final_score, wrong_count, pp_earned, hearts_deducted


def get_reading_explanation_from_ai(submission_id):
    """Gọi Gemini API để lấy giải thích cho bài Reading"""
    submission = Submission.query.get(submission_id)
    if not submission:
        return "Không tìm thấy bài nộp."

    exercise = ReadingExercise.query.get(submission.exercise_id)
    questions = exercise.questions

    prompt = f"""
        Bạn là một trợ giảng tiếng Anh IELTS/CEFR xuất sắc. Hãy giải thích chi tiết cho bài đọc dưới đây.
        ĐOẠN VĂN:
        {exercise.content}
        CÁC CÂU HỎI VÀ ĐÁP ÁN ĐÚNG:
        """

    for i, q in enumerate(questions, 1):
        # --- ĐOẠN MỚI: Truy vấn xem học sinh đã chọn đáp án nào ---
        chi_tiet = StudentReadingAnswer.query.filter_by(
            submission_id=submission_id,
            question_id=q.id
        ).first()

        selected = chi_tiet.selected_option if chi_tiet and chi_tiet.selected_option else "Không làm"

        prompt += f"""
            Câu {i}: {q.question_text}
            A. {q.option_a} | B. {q.option_b} | C. {q.option_c} | D. {q.option_d}
            => ĐÁP ÁN ĐÚNG: {q.correct_answer}
            => ĐÁP ÁN HỌC SINH CHỌN: {selected} 
            """

    prompt = f"""
        Bạn là một trợ giảng tiếng Anh IELTS/CEFR xuất sắc. Hãy giải thích chi tiết cho bài đọc dưới đây.
        ĐOẠN VĂN:
        {exercise.content}
        CÁC CÂU HỎI VÀ ĐÁP ÁN:
        """

    for i, q in enumerate(questions, 1):
        chi_tiet = StudentReadingAnswer.query.filter_by(
            submission_id=submission_id,
            question_id=q.id
        ).first()

        selected_letter = chi_tiet.selected_option if chi_tiet and chi_tiet.selected_option else None

        options_dict = {
            'A': q.option_a,
            'B': q.option_b,
            'C': q.option_c,
            'D': q.option_d
        }

        if selected_letter in options_dict:
            selected_text = f"{selected_letter}. {options_dict[selected_letter]}"
        else:
            selected_text = "Không làm (Bỏ trống)"

        correct_text = f"{q.correct_answer}. {options_dict[q.correct_answer]}"

        prompt += f"""
            Câu {i}: {q.question_text}
            A. {q.option_a} | B. {q.option_b} | C. {q.option_c} | D. {q.option_d}
            => ĐÁP ÁN ĐÚNG: {correct_text}
            => ĐÁP ÁN HỌC SINH CHỌN: {selected_text} 
            """

    prompt += """
        YÊU CẦU ĐẦU RA (SYSTEM INSTRUCTIONS):
        Bạn đóng vai trò là một hệ thống tự động trả về nội dung tĩnh. 
        TUYỆT ĐỐI KHÔNG chào hỏi, KHÔNG giới thiệu, KHÔNG kết luận, KHÔNG xưng hô.

        Hãy trả về kết quả tuân thủ CHÍNH XÁC cấu trúc Markdown dưới đây, bắt đầu ngay bằng trích dẫn đoạn văn:

        > [Trích dẫn lại nguyên văn đoạn đọc hiểu vào đây]

        ---

        ### Câu [Số thứ tự]: [Nội dung câu hỏi]
        * **Đáp án bạn chọn:** [Ghi lại toàn bộ nội dung đáp án học sinh chọn]
        * **Đáp án đúng:** [Ghi lại toàn bộ nội dung đáp án đúng]
        * **Dẫn chứng:** [Trích xuất chính xác 1-2 câu trong bài chứa thông tin trả lời]
        * **Giải thích:** [Phân tích trực tiếp, ngắn gọn vì sao đáp án đúng và chỉ ra bẫy ở các lựa chọn còn lại]
        * **Từ khóa/Mẹo:** [Nêu 1-2 từ vựng khóa hoặc kỹ năng áp dụng]

        (Tiếp tục lặp lại cấu trúc ### Câu... cho đến hết các câu hỏi)
        """

    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Lỗi khi gọi Trợ giảng AI: {str(e)}"


def grade_writing_with_ai(topic, essay_content):
    prompt = f"""
    Bạn là một giám khảo IELTS/CEFR chuyên nghiệp. Hãy chấm điểm bài viết tiếng Anh sau đây.

    ĐỀ BÀI: {topic.title}
    {topic.description}

    BÀI VIẾT CỦA HỌC SINH:
    {essay_content}

    YÊU CẦU ĐẦU RA (SYSTEM INSTRUCTIONS):
    1. Chấm điểm trên thang 100 cho 4 tiêu chí: Ngữ pháp, Từ vựng, Mạch lạc, và Đáp ứng yêu cầu (Task Response). 
    2. Điểm tổng (total_score) là trung bình cộng của 4 tiêu chí trên.
    3. Trả về nhận xét chi tiết bằng tiếng Việt vào trường ai_feedback.
    4. TUYỆT ĐỐI CHỈ TRẢ VỀ CHUẨN JSON NHƯ ĐỊNH DẠNG BÊN DƯỚI:
    {{
        "grammar_score": 85,
        "vocabulary_score": 80,
        "coherence_score": 90,
        "task_response_score": 85,
        "total_score": 85,
        "ai_feedback": "### Nhận xét chung\\nBài viết của bạn khá tốt...\\n\\n### Ưu điểm\\n- Từ vựng đa dạng...\\n\\n### Cần cải thiện\\n- Sai thì hiện tại đơn..."
    }}
    """

    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
        )

        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:-3].strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:-3].strip()

        return json.loads(raw_text)

    except Exception as e:
        print(f"Lỗi AI: {str(e)}")
        return None
