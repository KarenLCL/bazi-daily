/**
 * 专属命理工具 - 主JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // 初始化评分的环形渐变
    document.querySelectorAll('.score-circle[data-score]').forEach(function(el) {
        const score = parseInt(el.dataset.score);
        const color = score >= 80 ? '#4caf50' : 
                      score >= 65 ? '#8bc34a' : 
                      score >= 45 ? '#ffc107' : 
                      score >= 30 ? '#ff9800' : '#f44336';
        
        // 设置径向渐变
        el.style.background = `conic-gradient(${color} ${score * 3.6}deg, #f0f0f0 ${score * 3.6}deg)`;
        
        // 添加白色中心圆
        el.style.position = 'relative';
    });
    
    // 为日期跳转添加滑动支持
    let touchStartX = 0;
    let touchEndX = 0;
    
    const page = document.querySelector('.page-daily');
    if (page) {
        const dateStr = page.dataset.date;
        
        page.addEventListener('touchstart', function(e) {
            touchStartX = e.changedTouches[0].screenX;
        }, {passive: true});
        
        page.addEventListener('touchend', function(e) {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe(dateStr);
        }, {passive: true});
    }
    
    function handleSwipe(dateStr) {
        const threshold = 80;
        const diff = touchStartX - touchEndX;
        
        if (Math.abs(diff) > threshold) {
            const date = new Date(dateStr);
            if (diff > 0) {
                // 左滑 → 下一天
                date.setDate(date.getDate() + 1);
            } else {
                // 右滑 → 前一天
                date.setDate(date.getDate() - 1);
            }
            const y = date.getFullYear();
            const m = String(date.getMonth() + 1).padStart(2, '0');
            const d = String(date.getDate()).padStart(2, '0');
            window.location.href = `/date/${y}/${m}/${d}`;
        }
    }
    
});

/**
 * 设置评分（暴露给全局）
 */
function setRating(el) {
    const container = el.parentElement;
    const value = parseInt(el.dataset.value);
    const name = container.dataset.name;
    
    let hidden = container.querySelector('input[type="hidden"]');
    if (!hidden) {
        hidden = document.createElement('input');
        hidden.type = 'hidden';
        hidden.name = name;
        container.appendChild(hidden);
    }
    hidden.value = value;
    
    const stars = container.querySelectorAll('.star');
    stars.forEach((s, i) => {
        s.textContent = i < value ? '★' : '☆';
        s.classList.toggle('active', i < value);
    });
}

/**
 * 提交反馈（暴露给全局）
 */
function submitFeedback(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    
    const data = {};
    formData.forEach((value, key) => {
        if (key === 'actual_rating' || key === 'accuracy_rating') {
            data[key] = parseInt(value) || null;
        } else {
            data[key] = value;
        }
    });
    
    fetch('/api/feedback', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            alert('✅ 反馈已保存，谢谢！这将帮助算法更精准！');
            location.reload();
        } else {
            alert('保存失败: ' + (data.error || '未知错误'));
        }
    })
    .catch(err => alert('网络连接失败，请确保服务正在运行'));
    return false;
}

/**
 * 提交日记（暴露给全局）
 */
function submitDiary(event) {
    event.preventDefault();
    const form = document.getElementById('diary-form');
    if (!form) return false;
    
    const formData = new FormData(form);
    const data = {};
    formData.forEach((value, key) => {
        if (key === 'mood') data[key] = parseInt(value);
        else data[key] = value;
    });
    
    // date from page context
    const dateEl = document.querySelector('.page-daily') || document.querySelector('.page-diary');
    if (dateEl && dateEl.dataset.date) {
        data.date = dateEl.dataset.date;
    }
    
    fetch('/api/diary', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            const success = document.getElementById('diary-success');
            if (success) success.classList.remove('hidden');
            const input = document.querySelector('.diary-input');
            if (input) input.value = '';
            setTimeout(() => location.reload(), 1500);
        } else {
            alert('保存失败: ' + (data.error || '未知错误'));
        }
    })
    .catch(err => alert('网络连接失败'));
    return false;
}

/**
 * 编辑反馈（暴露给全局）
 */
function editFeedback() {
    const form = document.getElementById('feedback-form');
    if (form) form.classList.remove('hidden');
}
