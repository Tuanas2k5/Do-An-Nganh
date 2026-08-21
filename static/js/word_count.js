document.addEventListener('DOMContentLoaded', function() {
    const essayInput = document.getElementById('student_essay');
    const wordCountDisplay = document.getElementById('word-count');
    const wordCountBadge = document.getElementById('word-count-badge');
    const btnSubmit = document.getElementById('btn-submit');
    const validationMsg = document.getElementById('validation-msg');

    // Lấy số từ tối thiểu từ thuộc tính data-min-words của thẻ badge (dự phòng 150 nếu rỗng)
    const MIN_WORDS = parseInt(wordCountBadge.getAttribute('data-min-words')) || 150;

    function countWords(str) {
        return str.trim().split(/\s+/).filter(word => word.length > 0).length;
    }

    // Lắng nghe sự kiện người dùng gõ phím
    essayInput.addEventListener('input', function() {
        let currentWords = countWords(this.value);
        wordCountDisplay.textContent = currentWords;

        // Logic kiểm tra Đạt/Chưa đạt
        if (currentWords >= MIN_WORDS) {
            wordCountBadge.classList.replace('bg-secondary', 'bg-success');
            wordCountBadge.classList.replace('bg-danger', 'bg-success');
            btnSubmit.disabled = false;
            validationMsg.innerHTML = '<span class="text-success"><i class="fas fa-check-circle me-1"></i>Đã đủ số từ yêu cầu.</span>';
        } else {
            wordCountBadge.classList.replace('bg-success', currentWords > 0 ? 'bg-danger' : 'bg-secondary');
            btnSubmit.disabled = true;
            validationMsg.innerHTML = `<span class="text-danger"><i class="fas fa-exclamation-triangle me-1"></i>Cần viết thêm ít nhất ${MIN_WORDS - currentWords} từ nữa.</span>`;
        }
    });
});