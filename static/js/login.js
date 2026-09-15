document.addEventListener('DOMContentLoaded', function () {

    const togglePasswordBtn = document.getElementById('togglePassword');

    if (togglePasswordBtn) {
        togglePasswordBtn.addEventListener('click', function () {
            const passwordInput = document.getElementById('password');
            const eyeIcon = document.getElementById('eyeIcon');

            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                eyeIcon.classList.remove('fa-eye');
                eyeIcon.classList.add('fa-eye-slash');
            } else {
                passwordInput.type = 'password';
                eyeIcon.classList.remove('fa-eye-slash');
                eyeIcon.classList.add('fa-eye');
            }
        });
    }

    const loginForm = document.getElementById('loginForm');

    if (loginForm) {
        loginForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const submitBtn = document.getElementById('submitBtn');
            const errorDiv = document.getElementById('errorMessage');


            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Đang xử lý...';
            submitBtn.disabled = true;
            errorDiv.classList.add('d-none');

            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email: email, password: password })
                });

                const data = await response.json();

                if (response.ok) {
                    if (data.role === 'admin') {
                        window.location.href = '/admin/dashboard';
                    } else if (data.role === 'teacher') {
                        window.location.href = '/teacher/dashboard';
                    } else {
                        window.location.href = '/';
                    }
                } else {
                    errorDiv.textContent = data.msg || 'Tài khoản hoặc mật khẩu không chính xác!';
                    errorDiv.classList.remove('d-none');
                    submitBtn.innerHTML = '<i class="fas fa-arrow-right me-2"></i>ĐĂNG NHẬP';
                    submitBtn.disabled = false;
                }
            } catch (error) {
                errorDiv.textContent = 'Mất kết nối đến máy chủ. Vui lòng thử lại!';
                errorDiv.classList.remove('d-none');
                submitBtn.innerHTML = '<i class="fas fa-arrow-right me-2"></i>ĐĂNG NHẬP';
                submitBtn.disabled = false;
            }
        });
    }
});