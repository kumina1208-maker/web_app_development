/**
 * 互動式下廚模式 — 步驟切換、計時器、螢幕常亮
 * 供 recipes/cook.html 使用
 */

let currentStep = 1;
let totalSteps = 0;
let wakeLock = null;
let timerInterval = null;

document.addEventListener('DOMContentLoaded', function () {
    totalSteps = document.querySelectorAll('.cook-step').length;
    document.getElementById('total-steps').textContent = totalSteps;
    updateProgress();
    requestWakeLock();
});

// ── 步驟切換 ─────────────────────────────────────────────────
function nextStep() {
    if (currentStep < totalSteps) {
        showStep(currentStep + 1);
    }
}

function prevStep() {
    if (currentStep > 1) {
        showStep(currentStep - 1);
    }
}

function showStep(stepNum) {
    document.querySelectorAll('.cook-step').forEach(el => el.classList.remove('active'));
    document.querySelector(`.cook-step[data-step="${stepNum}"]`).classList.add('active');
    currentStep = stepNum;
    document.getElementById('current-step').textContent = currentStep;
    updateProgress();

    // 按鈕狀態
    document.getElementById('btn-prev').disabled = (currentStep === 1);
    if (currentStep === totalSteps) {
        document.getElementById('btn-next').style.display = 'none';
        document.getElementById('btn-finish').style.display = 'inline-block';
    } else {
        document.getElementById('btn-next').style.display = 'inline-block';
        document.getElementById('btn-finish').style.display = 'none';
    }
}

function updateProgress() {
    const pct = (currentStep / totalSteps) * 100;
    document.getElementById('progress-fill').style.width = pct + '%';
}

// ── 計時器 ───────────────────────────────────────────────────
function startTimer(seconds) {
    clearInterval(timerInterval);
    const display = document.getElementById('timer-display');
    const countdown = document.getElementById('timer-countdown');
    display.style.display = 'block';
    let remaining = seconds;
    countdown.textContent = remaining + ' 秒';

    timerInterval = setInterval(() => {
        remaining--;
        countdown.textContent = remaining + ' 秒';
        if (remaining <= 0) {
            clearInterval(timerInterval);
            countdown.textContent = '⏰ 時間到！';
        }
    }, 1000);
}

// ── 螢幕常亮 (Wake Lock API) ─────────────────────────────────
async function requestWakeLock() {
    try {
        if ('wakeLock' in navigator) {
            wakeLock = await navigator.wakeLock.request('screen');
            console.log('螢幕常亮已啟用');
        }
    } catch (err) {
        console.log('Wake Lock 不支援或被拒絕:', err);
    }
}

// 頁面離開時釋放
window.addEventListener('beforeunload', () => {
    if (wakeLock) wakeLock.release();
});
