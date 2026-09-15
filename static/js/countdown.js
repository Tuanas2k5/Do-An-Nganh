document.addEventListener('DOMContentLoaded', function () {
    const container = document.getElementById('timer-container');
    const display = document.getElementById('time-display');
    const form = document.getElementById('quiz-form') || document.getElementById('level-up-form');;

    if (!container || !display || !form) return;

    let timeLimitInMinutes = 15;

    if (container && container.hasAttribute('data-time')) {
        timeLimitInMinutes = parseInt(container.getAttribute('data-time'), 10);
    } else if (form.id === 'level-up-form') {
        timeLimitInMinutes = 60;
    }

   const storageKey = 'exam_end_time_' + window.location.pathname;
    let endTime = localStorage.getItem(storageKey);
    let now = new Date().getTime();

    if (!endTime || now > endTime) {
        endTime = now + timeLimitInMinutes * 60 * 1000;
        localStorage.setItem(storageKey, endTime);
    }

    function updateTimer() {
        let currentTime = new Date().getTime();
        let distance = endTime - currentTime;

        if (distance < 0) {
            clearInterval(timerInterval);
            localStorage.removeItem(storageKey);
            alert("Đã hết thời gian làm bài! Hệ thống sẽ tự động nộp.");
            form.noValidate = true;
            form.submit();
            return;
        }

        let minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        let seconds = Math.floor((distance % (1000 * 60)) / 1000);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;
        display.textContent = minutes + ":" + seconds;
    }

    let timerInterval = setInterval(updateTimer, 1000);
    updateTimer();

    form.addEventListener('submit', function() {
        localStorage.removeItem(storageKey);
    });
});