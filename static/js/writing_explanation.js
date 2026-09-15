document.addEventListener('DOMContentLoaded', function() {
    const feedbackBox = document.getElementById('ai-feedback-box');

    if (feedbackBox) {
        let rawFeedback = feedbackBox.getAttribute('data-feedback');

        if (rawFeedback && rawFeedback.trim() !== "") {
            rawFeedback = rawFeedback.replace(/&lt;/g, "<")
                                     .replace(/&gt;/g, ">")
                                     .replace(/&quot;/g, "\"")
                                     .replace(/&#39;/g, "'")
                                     .replace(/&amp;/g, "&");

            feedbackBox.innerHTML = marked.parse(rawFeedback);
        } else {
            feedbackBox.innerHTML = "<p class='text-muted'><i class='fas fa-info-circle me-1'></i>Chưa có nhận xét chi tiết từ hệ thống.</p>";
        }
    }

    const canvas = document.getElementById('scoreRadarChart');
    if (canvas) {
        const grammarScore = parseFloat(canvas.getAttribute('data-grammar')) || 0;
        const vocabScore = parseFloat(canvas.getAttribute('data-vocabulary')) || 0;
        const coherenceScore = parseFloat(canvas.getAttribute('data-coherence')) || 0;
        const taskScore = parseFloat(canvas.getAttribute('data-task')) || 0;

        const ctx = canvas.getContext('2d');
        new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Ngữ Pháp', 'Từ Vựng', 'Mạch Lạc', 'Đáp Ứng Đề'],
                datasets: [{
                    label: 'Điểm số',
                    data: [grammarScore, vocabScore, coherenceScore, taskScore],
                    backgroundColor: 'rgba(13, 110, 253, 0.2)',
                    borderColor: 'rgba(13, 110, 253, 1)',
                    pointBackgroundColor: 'rgba(13, 110, 253, 1)',
                    borderWidth: 2,
                    pointRadius: 4
                }]
            },
            options: {
                scales: {
                    r: {
                        angleLines: { display: true },
                        suggestedMin: 0,
                        suggestedMax: 100,
                        ticks: { stepSize: 20 }
                    }
                },
                plugins: {
                    legend: { display: false }
                },
                maintainAspectRatio: false
            }
        });
    }
});