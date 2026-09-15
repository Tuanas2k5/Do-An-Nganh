document.addEventListener('DOMContentLoaded', function() {
    const btnExplain = document.getElementById('btn-explain-ai');
    const feedbackContainer = document.getElementById('ai-feedback-container');
    const feedbackContent = document.getElementById('ai-feedback-content');

    if (!btnExplain) return;

    const submissionId = btnExplain.getAttribute('data-id');

    const originalBtnHTML = btnExplain.innerHTML;

    btnExplain.addEventListener('click', function() {
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

        fetch(`/exams/api/reading/explain/${submissionId}`)
            .then(response => response.json())
            .then(result => {
                if(result.status === 'success') {
                    feedbackContent.innerHTML = `<div class="ai-explanation fs-6 text-dark" style="line-height: 1.8;">${marked.parse(result.data)}</div>`;
                    btnExplain.innerHTML = '<i class="fas fa-check me-2"></i>Đã Phân Tích Xong';
                } else {
                    feedbackContent.innerHTML = `<div class="alert alert-danger mb-0 shadow-sm"><i class="fas fa-exclamation-triangle me-2"></i>${result.message}</div>`;
                    btnExplain.disabled = false;
                    btnExplain.innerHTML = originalBtnHTML;
                }
            })
            .catch(error => {
                console.error(error);
                feedbackContent.innerHTML = `<div class="alert alert-danger mb-0 shadow-sm"><i class="fas fa-wifi me-2"></i>Đã có lỗi kết nối mạng. Vui lòng thử lại!</div>`;
                btnExplain.disabled = false;
                btnExplain.innerHTML = originalBtnHTML;
            });
    });
});