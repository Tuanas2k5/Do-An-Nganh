document.addEventListener('DOMContentLoaded', function() {
    const btnExplain = document.getElementById('btn-explain-ai');
    const feedbackContainer = document.getElementById('ai-feedback-container');
    const feedbackContent = document.getElementById('ai-feedback-content');

    // Kiểm tra xem nút có tồn tại không để tránh lỗi ở các trang khác
    if (!btnExplain) return;

    // Lấy ID bài nộp từ thuộc tính data-id của thẻ HTML
    const submissionId = btnExplain.getAttribute('data-id');

    btnExplain.addEventListener('click', function() {
        // 1. Hiển thị trạng thái loading
        btnExplain.disabled = true;
        btnExplain.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Trợ giảng đang phân tích...';

        feedbackContainer.classList.remove('d-none');
        feedbackContent.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-3 text-muted">Vui lòng chờ khoảng 5-10 giây để AI đọc đoạn văn và phân tích đáp án nhé...</p>
            </div>
        `;

        // 2. Gọi API ngầm lên server
        fetch(`/exams/api/reading/explain/${submissionId}`)
            .then(response => response.json())
            .then(result => {
                if(result.status === 'success') {
                    // Dùng div với white-space: pre-wrap để giữ nguyên định dạng của Gemini
                    feedbackContent.innerHTML = `<div class="ai-explanation fs-6 text-dark" style="line-height: 1.8;">${marked.parse(result.data)}</div>`;
                } else {
                    feedbackContent.innerHTML = `<div class="alert alert-danger">${result.message}</div>`;
                }
            })
            .catch(error => {
                console.error(error);
                feedbackContent.innerHTML = `<div class="alert alert-danger">Đã có lỗi kết nối mạng. Vui lòng thử lại!</div>`;
            })
            .finally(() => {
                // Phục hồi lại nút bấm
                btnExplain.disabled = false;
                btnExplain.innerHTML = '<i class="fas fa-check me-2"></i>Đã Phân Tích Xong';
            });
    });
});