# Ứng dụng hỗ trợ học tiếng Anh 

## I. Mô tả

LearnEng là dự án cá nhân trong khuôn khổ Đồ án ngành, tập trung xây dựng một nền tảng tự học tiếng Anh tích hợp AI, đóng vai trò như một trợ giảng ảo tự động đánh giá và phản hồi kết quả cho hai kỹ năng Reading và Writing. Hệ thống được thiết kế để phục vụ các nhóm đối tượng cốt lõi bao gồm: Quản trị viên (Admin) quản lý hệ thống, Giáo viên tạo và quản lý ngân hàng bài tập, và Học sinh thực hiện việc làm bài, nhận giải thích từ AI. Hệ thống giải quyết bài toán thiếu nguồn lực giáo viên chấm bài tiểu luận thủ công bằng cách ứng dụng Google Gemini API để tự động hóa khâu đánh giá dựa trên thang điểm IELTS/CEFR.

## II. Công nghệ sử dụng

- Web framework: Flask 3.1
- Database: MySQL (PyMySQL + SQLAlchemy)
- Authentication: Flask-Login, Flask-JWT-Extended
- Storage: Cloudinary
- Testing: Pytest, pytest-cov
- Version control: Git + GitHub

## III. Các phiên bản release

| Mã phiên bản | Nội dung | Trạng thái |
|--------------|----------|------------|
|              |          |            |

## IV. Cấu trúc tổng quan

<pre>
Do-An-Nganh/
├── modules/
│   ├── users/
│   │   ├── models.py
│   │   ├── views.py
│   │   └── services.py
│   ├── exams/
│   │   ├── models.py
│   │   ├── views.py
│   │   └── services.py
│   ├── teacher/
│   │   └── views.py
│   └── admin/
│       └── views.py
├── utils/
│   ├── utils.py
│   └── validators.py
├── static/
├── templates/
├── tests/
│   ├── conftest.py
│   ├── test_users.py
│   ├── test_exams_exercises.py
│   ├── test_teachers.py
│   └── test_admin.py
├── __init__.py
├── index.py
├── admin.py
├── extensions.py
├── seed.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
</pre>

## V. Cài đặt và chạy

### 1. Yêu cầu

- Python 3.10 trở lên
- Git
- MySQL

### 2. Hướng dẫn chạy

- Đối với chạy ứng dụng

<pre>
Bước 1: Đứng tại thư mục gốc của repository
Bước 2: Tạo và kích hoạt môi trường ảo
         python -m venv venv
         venv\Scripts\Activate
Bước 3: Cài đặt các thư viện
         pip install -r requirements.txt
Bước 4: Tạo file .env từ .env.example và điền thông tin kết nối database
Bước 5: Chạy ứng dụng
         python index.py
</pre>

- Đối với chạy kiểm thử

<pre>
Bước 1: Đứng tại thư mục gốc của repository
Bước 2: Mở command prompt
Bước 3: venv\Scripts\Activate (nếu chưa thực hiện)
Bước 4: Nhập pytest -v
</pre>

### 3. Truy cập

- Local: http://localhost:8000
- Production: Chưa triển khai