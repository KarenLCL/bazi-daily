"""
🌟 Karen 专属命理工具 - 单文件自包含服务器
无需 pip install，无需任何第三方库，只需要 Python 3。
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import date, datetime, timedelta
from urllib.parse import urlparse, parse_qs
import json, os, sys, sqlite3, math, calendar, hashlib, hmac, secrets

# ============ 添加项目路径 ============
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bazi_engine import (
    HEAVENLY_STEMS, EARTHLY_BRANCHES,
    get_day_stem_branch, calculate_daily_bazi,
    calculate_daily_score, compare_with_birth_chart,
    get_bazi_pillar_name, get_five_element_from_stem,
    get_five_element_from_branch, get_ten_god,
    get_hour_branch_from_time, get_year_stem_branch,
    get_month_stem_branch,
)
from user_profile import PROFILE, BIRTH_CHART, get_current_dayun
from interpreter import PersonalizedInterpreter
from database import (
    init_db, save_daily_feedback, save_diary_entry,
    get_feedback_by_date, get_recent_feedback,
    get_diary_entries, get_feedback_accuracy_stats,
)
from plans_module import (
    add_plan, get_plans_by_date, get_upcoming_plans,
    get_recent_plans, delete_plan,
)

interpreter = PersonalizedInterpreter()
HOST = '0.0.0.0'
PORT = int(os.environ.get('PORT', 5000))

# ============ 密码认证配置 ============
AUTH_PASSWORD = "Karen0206"
AUTH_SALT = "bazi_daily_2026_karen"
COOKIE_NAME = "BAZI_AUTH"

def make_auth_token():
    """生成认证令牌"""
    raw = f"{AUTH_PASSWORD}:{AUTH_SALT}:{date.today().isoformat()[:7]}"
    return hashlib.sha256(raw.encode()).hexdigest()

def check_auth(cookies_str):
    """检查认证cookie是否有效"""
    if not cookies_str:
        return False
    for part in cookies_str.split(';'):
        part = part.strip()
        if part.startswith(f"{COOKIE_NAME}="):
            token = part.split('=', 1)[1]
            return token == make_auth_token()
    return False

# ============================================================
#  HTML 模板
# ============================================================

HTML_HEAD = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>🌟 专属命理 · Karen</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;background:#f5f5f5;color:#333;line-height:1.6;padding-top:56px;padding-bottom:60px}
a{text-decoration:none;color:inherit}
.top-nav{position:fixed;top:0;left:0;right:0;height:56px;background:#fff;border-bottom:1px solid #e0e0e0;z-index:100;display:flex;align-items:center}
.nav-inner{max-width:600px;margin:0 auto;width:100%;display:flex;align-items:center;justify-content:space-between;padding:0 12px}
.nav-logo{font-size:18px;font-weight:700;color:#5d4037}
.nav-links{display:flex;gap:4px}
.nav-item{padding:8px 12px;border-radius:20px;font-size:14px;color:#666;transition:all .2s}
.nav-item.active{background:#5d4037;color:#fff;font-weight:600}
.container{max-width:600px;margin:0 auto;padding:16px 12px}
.card{background:#fff;border-radius:16px;padding:20px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,.08)}
.card-header{display:flex;align-items:center;gap:8px;margin-bottom:12px}
.card-icon{font-size:20px}
.card-title{font-size:16px;font-weight:600;color:#333;flex:1}
.card-badge{font-size:12px;padding:2px 10px;border-radius:12px;background:#efebe9;color:#5d4037}
.card-text{font-size:15px;color:#444;line-height:1.7;margin-bottom:6px}
.card-sub{font-size:13px;color:#888}
.card-highlight{border-left:4px solid #ff8f00;background:#fff8e1}
.card-reminder{background:#f5f0eb}
.date-nav{display:flex;align-items:center;justify-content:space-between;padding:12px 0;margin-bottom:8px;position:sticky;top:56px;z-index:50;background:#f5f5f5}
.date-arrow{font-size:28px;padding:8px 16px;color:#999;user-select:none}
.date-center{text-align:center}
.date-main{font-size:20px;font-weight:700;color:#333}
.date-weekday{font-size:13px;color:#888}
.date-lunar{font-size:12px;color:#aaa;display:block}
.score-card{border-radius:16px;padding:20px;margin-bottom:16px;display:flex;align-items:center;gap:20px}
.score-circle{width:76px;height:76px;border-radius:50%;background:rgba(255,255,255,.9);display:flex;flex-direction:column;align-items:center;justify-content:center;flex-shrink:0;box-shadow:0 2px 8px rgba(0,0,0,.08)}
.score-number{font-size:28px;font-weight:800;color:#333;line-height:1}
.score-label{font-size:12px;color:#888}
.score-info{flex:1}
.score-level{font-size:20px;font-weight:700;margin-bottom:4px}
.score-pillar{font-size:14px;color:#555;margin-bottom:2px}
.score-element{font-size:13px;color:#888}
.score-level.da-ji{color:#bf8f00}.score-level.ji{color:#8d6e00}.score-level.ping{color:#5d4037}.score-level.bu-jia{color:#795548}.score-level.jin-shen{color:#4e342e}
.tag-row{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.tag{font-size:12px;padding:4px 12px;border-radius:12px;background:#f5f5f5;color:#666}
.tag-good{background:#fff8e1;color:#8d6e00}
.tag-bad{background:#efebe9;color:#795548}
.tag-info{background:#e3f2fd;color:#1565c0}
.advice-col{display:flex;gap:16px}
.advice-good,.advice-bad{flex:1}
.advice-good h4,.advice-bad h4{font-size:14px;margin-bottom:8px}
.advice-good ul,.advice-bad ul{padding-left:16px}
.advice-good li,.advice-bad li{font-size:14px;color:#555;margin-bottom:4px}
.feedback-input{width:100%;padding:12px;border:1px solid #e0e0e0;border-radius:12px;font-size:14px;font-family:inherit;resize:vertical;margin-bottom:12px}
.feedback-input:focus{outline:none;border-color:#5d4037}
.feedback-ratings{display:flex;gap:20px;margin-bottom:12px;flex-wrap:wrap}
.rating-group{flex:1;min-width:140px}
.rating-group label{font-size:13px;color:#666;display:block;margin-bottom:4px}
.stars{font-size:28px;cursor:pointer;display:flex;gap:4px}
.star{color:#ddd;transition:color .15s;padding:2px}
.star.active,.star.active~.star{color:#ff8f00}
.star:hover,.star:hover~.star{color:#ffb300}
.star-hint{font-size:11px;color:#aaa;margin-top:2px;display:block}
.btn{padding:10px 24px;border:none;border-radius:12px;font-size:15px;font-weight:600;cursor:pointer;transition:all .2s}
.btn-primary{background:#5d4037;color:#fff;width:100%}
.btn-primary:hover{background:#4e342e}
.btn-primary:active{transform:scale(.98)}
.btn-sm{padding:6px 16px;font-size:13px;background:#e0e0e0;color:#333;margin-top:8px}
.footer{text-align:center;padding:24px 16px;font-size:13px;color:#aaa}
.footer-small{font-size:11px;margin-top:4px}
@media(max-width:400px){.advice-col{flex-direction:column}}
.mini-calendar{display:grid;grid-template-columns:repeat(7,1fr);gap:4px}
.mini-day{display:flex;flex-direction:column;align-items:center;padding:6px 2px;border-radius:8px;font-size:12px;text-align:center}
.mini-day-num{font-weight:600;font-size:14px}
.mini-day-score{font-size:10px;color:#666}
.date-list{display:flex;flex-direction:column;gap:8px}
.date-item{display:flex;align-items:center;padding:10px 14px;border-radius:12px;gap:12px}
.date-good{background:#fff8e1}
.date-bad{background:#efebe9}
.date-day{font-weight:600;font-size:14px;flex:1}
.date-pillar{font-size:13px;color:#666}
.date-score{font-size:16px;font-weight:700}
.month-chart{display:flex;align-items:flex-end;gap:6px;height:140px;padding:0 4px}
.month-bar-wrapper{flex:1;display:flex;flex-direction:column;align-items:center;height:100%;justify-content:flex-end}
.month-bar{width:100%;max-width:24px;border-radius:4px 4px 0 0;min-height:4px}
.month-label{font-size:10px;color:#888;margin-top:4px}
.month-score{font-size:9px;color:#aaa}
.month-detail-list{display:flex;flex-direction:column;gap:4px}
.month-detail-item{display:flex;align-items:center;padding:8px 12px;border-radius:8px;gap:8px}
.month-detail-item:nth-child(odd){background:#fafafa}
.month-detail-name{font-weight:600;width:40px;font-size:14px}
.month-detail-pillar{font-size:13px;color:#888;flex:1}
.month-detail-level{font-size:13px;font-weight:500}
.month-detail-score{font-size:14px;font-weight:600;color:#555;width:40px;text-align:right}
.stats-row{display:flex;gap:12px;margin-bottom:16px}
.stat-card{flex:1;background:#fff;border-radius:16px;padding:16px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.08)}
.stat-number{font-size:28px;font-weight:800;color:#5d4037}
.stat-label{font-size:12px;color:#888;margin-top:4px}
.diary-input{width:100%;padding:14px;border:1px solid #e0e0e0;border-radius:12px;font-size:15px;font-family:inherit;resize:vertical;min-height:100px;line-height:1.6}
.diary-input:focus{outline:none;border-color:#5d4037}
.diary-extras{display:flex;gap:16px;margin:12px 0;flex-wrap:wrap}
.diary-mood,.diary-category{display:flex;align-items:center;gap:8px}
.diary-mood label,.diary-category label{font-size:14px;color:#666}
.mood-select,.category-select{padding:8px 12px;border:1px solid #e0e0e0;border-radius:8px;font-size:14px;background:#fff;color:#333}
.diary-list{display:flex;flex-direction:column;gap:12px}
.diary-item{padding:14px;background:#fafafa;border-radius:12px}
.diary-item-header{display:flex;align-items:center;gap:8px;margin-bottom:8px;flex-wrap:wrap}
.diary-date{font-weight:600;font-size:14px;color:#333}
.diary-time{font-size:12px;color:#aaa}
.diary-cat-badge{font-size:11px;padding:2px 8px;border-radius:8px;background:#e0e0e0;color:#555}
.diary-content{font-size:14px;color:#555;line-height:1.5}
.feedback-list{display:flex;flex-direction:column;gap:12px}
.feedback-item{padding:12px;background:#fafafa;border-radius:12px}
.fb-header{display:flex;align-items:center;gap:8px;margin-bottom:6px}
.fb-date{font-size:14px;font-weight:600;color:#5d4037}
.fb-level{font-size:11px;padding:2px 8px;border-radius:8px}
.fb-score{font-size:13px;color:#666}
.fb-content{font-size:14px;color:#555;line-height:1.5}
.fb-ratings{display:flex;gap:16px;font-size:12px;color:#888;margin-top:4px}
.page-title{font-size:22px;font-weight:700;color:#333;margin-bottom:4px}
.page-subtitle{font-size:14px;color:#888;margin-bottom:16px}
.hidden{display:none!important}
</style>
</head>
<body>
<div class="top-nav"><div class="nav-inner">
<a href="/" class="nav-logo">🌟 命理</a>
<div class="nav-links">
<a href="/" class="nav-item NAV_HOME">今日</a>
<a href="/monthly" class="nav-item NAV_MONTHLY">本月</a>
<a href="/yearly" class="nav-item NAV_YEARLY">本年</a>
<a href="/diary" class="nav-item NAV_DIARY">日记</a>
<a href="/history" class="nav-item NAV_HISTORY">记录</a>
</div></div></div>
<main class="container">
'''

HTML_FOOT = '''</main>
<footer class="footer"><p>✨ 辛金日主 · 喜土金 · 忌木火</p>
<p class="footer-small">专属定制 · 基于已验证命盘</p></footer>
<script>
function setRating(el){var c=el.parentElement,v=parseInt(el.dataset.value),n=c.dataset.name;var h=c.querySelector('input[type=hidden]');if(!h){h=document.createElement('input');h.type='hidden';h.name=n;c.appendChild(h)}h.value=v;var s=c.querySelectorAll('.star');s.forEach(function(x,i){x.textContent=i<v?'★':'☆';x.classList.toggle('active',i<v)})}
function submitFeedback(e){e.preventDefault();var f=e.target,d={};new FormData(f).forEach(function(v,k){if(k==='actual_rating'||k==='accuracy_rating')d[k]=parseInt(v)||null;else d[k]=v});fetch('/api/feedback',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)}).then(function(r){return r.json()}).then(function(d){if(d.status==='ok'){alert('✅ 反馈已保存！');location.reload()}else alert('保存失败: '+d.error}).catch(function(){alert('网络错误')});return false}
function submitDiary(e){e.preventDefault();var f=document.getElementById('diary-form'),d={};new FormData(f).forEach(function(v,k){if(k==='mood')d[k]=parseInt(v);else d[k]=v});fetch('/api/diary',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)}).then(function(r){return r.json()}).then(function(d){if(d.status==='ok'){alert('✅ 日记已保存！');location.reload()}else alert('保存失败: '+d.error}).catch(function(){alert('网络错误')});return false}
function editFeedback(){document.getElementById('feedback-form').classList.remove('hidden')}
function toggleVoiceInput(){var t=document.getElementById('diary-input');var s=document.getElementById('voice-status');if(!window.SpeechRecognition&&!window.webkitSpeechRecognition){alert('您的浏览器不支持语音输入。建议使用Chrome浏览器，或者用手机自带的语音键盘输入。');return}var r=window.SpeechRecognition||window.webkitSpeechRecognition;var rec=new r();rec.lang='zh-CN';rec.interimResults=true;var btn=document.getElementById('voice-btn');btn.textContent='⏹️';btn.style.borderColor='#c62828';s.style.display='block';rec.onresult=function(e){var res='';for(var i=e.resultIndex;i<e.results.length;i++){if(e.results[i].isFinal)res+=e.results[i][0].transcript}t.value+=res};rec.onend=function(){btn.textContent='🎤';btn.style.borderColor='#e0e0e0';s.style.display='none'};rec.onerror=function(){btn.textContent='🎤';btn.style.borderColor='#e0e0e0';s.style.display='none';alert('语音识别出错，请重试或使用手机语音键盘输入')};rec.start()}
function submitPlan(e){e.preventDefault();var f=document.getElementById('plan-form'),d={};new FormData(f).forEach(function(v,k){d[k]=v});fetch('/api/plans',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)}).then(function(r){return r.json()}).then(function(d){if(d.status==='ok'){alert('✅ 已记录！');location.reload()}else alert('添加失败: '+d.error}).catch(function(){alert('网络错误')});return false}
function deletePlan(id){if(!confirm('确定删除这条记录？'))return;fetch('/api/plans/'+id,{method:'DELETE'}).then(function(r){return r.json()}).then(function(d){if(d.status==='ok'){location.reload()}else alert('删除失败')})}
</script>
</body></html>'''

LOGIN_PAGE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>🌟 专属命理 · 登录</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;background:linear-gradient(135deg,#5d4037,#3e2723);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
.login-card{background:#fff;border-radius:20px;padding:40px 32px;max-width:380px;width:100%;box-shadow:0 20px 60px rgba(0,0,0,.3)}
.login-icon{text-align:center;font-size:48px;margin-bottom:12px}
.login-title{text-align:center;font-size:22px;font-weight:700;color:#3e2723;margin-bottom:4px}
.login-sub{text-align:center;font-size:14px;color:#888;margin-bottom:28px}
.login-input{width:100%;padding:14px 16px;border:2px solid #e0e0e0;border-radius:12px;font-size:16px;font-family:inherit;transition:border-color .2s;margin-bottom:16px}
.login-input:focus{outline:none;border-color:#5d4037}
.login-btn{width:100%;padding:14px;background:#5d4037;color:#fff;border:none;border-radius:12px;font-size:16px;font-weight:600;cursor:pointer;transition:background .2s}
.login-btn:hover{background:#3e2723}
.login-btn:active{transform:scale(.98)}
.login-error{color:#c62828;font-size:14px;text-align:center;margin-bottom:12px;display:none}
.login-hint{text-align:center;font-size:12px;color:#aaa;margin-top:20px}
</style>
</head>
<body>
<div class="login-card">
<div class="login-icon">🔮</div>
<div class="login-title">专属命理</div>
<div class="login-sub">输入密码查看今日运势</div>
<form method="POST" action="/login" onsubmit="return validateLogin(event)">
<div class="login-error" id="login-error">密码错误，请重试</div>
<input type="password" name="password" class="login-input" placeholder="请输入密码" autofocus>
<button type="submit" class="login-btn">🌟 进入</button>
</form>
<div class="login-hint">专属于 Karen · 请勿分享</div>
</div>
<script>
function validateLogin(e){var p=document.querySelector('input[name=password]').value.trim();if(!p){e.preventDefault();document.getElementById('login-error').style.display='block';document.getElementById('login-error').textContent='请输入密码';return false}return true}
var urlParams=new URLSearchParams(window.location.search);if(urlParams.get('error')==='1'){document.getElementById('login-error').style.display='block'}
</script>
</body>
</html>'''

WEEKDAY_NAMES = ['周一','周二','周三','周四','周五','周六','周日']
LEVEL_CLASSES = {'大吉':'da-ji','吉':'ji','平':'ping','不佳':'bu-jia','谨慎':'jin-shen'}

# ============================================================
#  HTTP 处理器
# ============================================================

class BaziHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            params = parse_qs(parsed.query)
            
            # 登录页面无需认证
            if path == '/login':
                self._send_html(LOGIN_PAGE)
                return
            
            # 检查认证
            cookies = self.headers.get('Cookie', '')
            if not check_auth(cookies):
                self._redirect('/login')
                return
            
            if path == '/':
                self._serve_daily(date.today())
            elif path.startswith('/date/'):
                parts = path.split('/')
                if len(parts) >= 4:
                    y, m, d = int(parts[2]), int(parts[3]), int(parts[4])
                    self._serve_daily(date(y, m, d))
                else:
                    self._serve_daily(date.today())
            elif path == '/monthly':
                today = date.today()
                y = int(params.get('year', [today.year])[0])
                m = int(params.get('month', [today.month])[0])
                self._serve_monthly(y, m)
            elif path == '/yearly':
                today = date.today()
                y = int(params.get('year', [today.year])[0])
                self._serve_yearly(y)
            elif path == '/diary':
                self._serve_diary()
            elif path == '/history':
                self._serve_history()
            elif path.startswith('/api/'):
                # API也需认证
                self._serve_api(path, params)
            else:
                self._serve_daily(date.today())
        except Exception as e:
            self._send_text(500, f"Error: {e}")
    
    def _redirect(self, path):
        """重定向"""
        self.send_response(302)
        self.send_header('Location', path)
        self.end_headers()
    
    def do_POST(self):
        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len) if content_len > 0 else b''
        
        parsed = urlparse(self.path)
        path = parsed.path
        
        # 登录处理
        if path == '/login':
            # 解析 form data
            try:
                body_str = body.decode('utf-8')
                form_data = parse_qs(body_str)
                password = form_data.get('password', [''])[0]
                
                if password == AUTH_PASSWORD:
                    # 设置cookie (30天过期)
                    self.send_response(302)
                    self.send_header('Location', '/')
                    token = make_auth_token()
                    expires = (datetime.now() + timedelta(days=30)).strftime('%a, %d %b %Y %H:%M:%S GMT')
                    self.send_header('Set-Cookie', f'{COOKIE_NAME}={token}; Path=/; Max-Age=2592000; SameSite=Lax')
                    self.end_headers()
                else:
                    self.send_response(302)
                    self.send_header('Location', '/login?error=1')
                    self.end_headers()
            except Exception:
                self.send_response(302)
                self.send_header('Location', '/login?error=1')
                self.end_headers()
            return
        
        # API接口需要认证
        cookies = self.headers.get('Cookie', '')
        if not check_auth(cookies):
            self._send_json({'error': 'unauthorized'}, 401)
            return
        
        try:
            data = json.loads(body) if body else {}
            
            if path == '/api/feedback':
                result = save_daily_feedback({
                    'date': data.get('date', date.today().isoformat()),
                    'prediction_score': data.get('prediction_score'),
                    'prediction_level': data.get('prediction_level'),
                    'actual_feedback': data.get('actual_feedback', ''),
                    'actual_rating': data.get('actual_rating'),
                    'accuracy_rating': data.get('accuracy_rating'),
                })
                self._send_json({'status': 'ok' if result else 'error'})
            
            elif path == '/api/diary':
                result = save_diary_entry({
                    'date': data.get('date', date.today().isoformat()),
                    'entry_time': datetime.now().strftime('%H:%M'),
                    'content': data.get('content', ''),
                    'mood': data.get('mood'),
                    'category': data.get('category', '日常'),
                })
                self._send_json({'status': 'ok' if result else 'error'})
            
            elif path == '/api/plans':
                result = add_plan(data)
                self._send_json({'status': 'ok' if result else 'error'})
            else:
                self._send_json({'error': 'not found'}, 404)
        except Exception as e:
            self._send_json({'error': str(e)}, 500)
    
    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path.startswith('/api/plans/'):
            plan_id = int(path.split('/')[-1])
            result = delete_plan(plan_id)
            self._send_json({'status': 'ok' if result else 'error'})
    
    def _send_html(self, html):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def _send_json(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def _send_text(self, code, text):
        self.send_response(code)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(str(text).encode('utf-8'))
    
    def _page(self, content, active_nav=''):
        nav_class = {'home':'','monthly':'','yearly':'','diary':'','history':''}
        if active_nav in nav_class:
            nav_class[active_nav] = 'active'
        html = HTML_HEAD
        for k, v in nav_class.items():
            html = html.replace(f'NAV_{k.upper()}', v)
        html += content + HTML_FOOT
        return html
    
    # ============================================================
    #  每日运势
    # ============================================================
    
    def _serve_daily(self, target_date):
        reading = interpreter.generate_daily_reading(target_date)
        fb = get_feedback_by_date(target_date.isoformat())
        r = reading
        i = r['interpretation']
        o = i['overview']
        c = i['career']
        rel = i['relationship']
        h = i['health']
        fam = i['family']
        adv = i['advice']
        rem = i['reminders']
        hr = reading['hour_reading']
        s = reading['score']
        
        lev_class = LEVEL_CLASSES.get(s['level'], 'ping')
        
        prev_d = target_date - timedelta(days=1)
        next_d = target_date + timedelta(days=1)
        
        content = f'''
        <div class="date-nav">
        <a href="/date/{prev_d.strftime('%Y/%m/%d')}" class="date-arrow">‹</a>
        <div class="date-center">
        <h2 class="date-main">{target_date.strftime('%Y年%m月%d日')}</h2>
        <span class="date-weekday">{WEEKDAY_NAMES[target_date.weekday()]}</span>
        <span class="date-lunar">{o.get('lunar_info',{}).get('lunar_month','')}</span>
        </div>
        <a href="/date/{next_d.strftime('%Y/%m/%d')}" class="date-arrow">›</a>
        </div>
        
        <div class="score-card" style="background:{s['color']}">
        <div class="score-circle" style="background:conic-gradient(#5d4037 {s['score']*3.6}deg,#f0f0f0 {s['score']*3.6}deg)">
        <div class="score-number">{s['score']}</div>
        <div class="score-label">分</div></div>
        <div class="score-info">
        <div class="score-level {lev_class}">{s['level']}</div>
        <div class="score-pillar">{r['daily_bazi']['day']['name']} · {r['daily_bazi']['day']['nayin']}</div>
        <div class="score-element">天干{o['stem_element']} · 地支{o['branch_element']}</div>
        </div></div>
        
        <div class="card"><div class="card-header"><span class="card-icon">📋</span><span class="card-title">今日总览</span></div>
        <p class="card-text">{o['summary']}</p>
        <p class="card-text card-sub">{o.get('element_note','')}</p></div>
        
        <div class="card card-highlight"><div class="card-header"><span class="card-icon">🔄</span><span class="card-title">大运 · {reading['current_dayun']['name']}</span>
        <span class="card-badge">{reading['current_dayun']['age']}岁</span></div>
        <p class="card-text">{c['dayun_effect']}</p></div>
        
        <div class="card"><div class="card-header"><span class="card-icon">💼</span><span class="card-title">事业财运</span></div>
        <p class="card-text">{c['ten_god_reading']}</p>'''
        
        for effect in c.get('branch_effects', []):
            content += f'<p class="card-text card-sub" style="color:#e65100">⚠ {effect}</p>'
        
        content += f'''
        <div class="tag-row">
        <span class="tag {"tag-good" if c["is_favorable_day"] else "tag-bad"}">{"✅ 用神日" if c["is_favorable_day"] else "⚠ 忌神日"}</span>
        <span class="tag tag-info">十神: {c["ten_god"]}</span>
        </div></div>
        
        <div class="card"><div class="card-header"><span class="card-icon">💕</span><span class="card-title">感情人际</span></div>
        <p class="card-text">{rel['ten_god_reading']}</p>
        <p class="card-text card-sub">{rel['gu_chen_tip']}</p></div>
        
        <div class="card"><div class="card-header"><span class="card-icon">🏥</span><span class="card-title">健康提示</span></div>'''
        for tip in h['tips']:
            content += f'<p class="card-text">• {tip}</p>'
        content += '<details class="card-details"><summary>个人体质提示</summary>'
        for tip in h['personal_tips']:
            content += f'<p class="card-text card-sub">• {tip}</p>'
        content += '</details></div>'
        
        content += f'''
        <div class="card"><div class="card-header"><span class="card-icon">👨‍👩‍👧</span><span class="card-title">父母 / 家庭</span></div>'''
        for note in fam['notes']:
            content += f'<p class="card-text">• {note}</p>'
        
        # ---- 今日计划 ----
        today_plans = get_plans_by_date(target_date.isoformat())
        if today_plans:
            content += '<div class="card card-highlight"><div class="card-header"><span class="card-icon">📌</span><span class="card-title">今日安排</span></div>'
            for plan in today_plans:
                content += f'<p class="card-text">• <strong>{plan["title"]}</strong>'
                if plan.get('description'):
                    content += f'：{plan["description"]}'
                content += f' <span class="tag" style="font-size:11px">{plan.get("category","")}</span></p>'
            content += '</div>'
        
        content += f'''
        <div class="card"><div class="card-header"><span class="card-icon">✅</span><span class="card-title">今日宜忌</span></div>
        <div class="advice-col">
        <div class="advice-good"><h4>✅ 宜</h4><ul>'''
        for item in adv['favorable'][:5]:
            content += f'<li>{item}</li>'
        content += '</ul></div><div class="advice-bad"><h4>❌ 不宜</h4><ul>'
        for item in adv['unfavorable'][:5]:
            content += f'<li>{item}</li>'
        content += '</ul></div></div></div>'
        
        content += f'''
        <div class="card card-reminder"><div class="card-header"><span class="card-icon">🔔</span><span class="card-title">专属提醒</span></div>'''
        for reminder in rem:
            content += f'<p class="card-text">• {reminder}</p>'
        content += '</div>'
        
        content += f'''
        <div class="card"><div class="card-header"><span class="card-icon">🌅</span><span class="card-title">晨起 · 辰时 (7-9点)</span></div>
        <p class="card-text">{hr["description"]}</p>
        <p class="card-text card-sub">{hr["ten_god_reading"]}</p></div>
        
        <div class="card card-feedback" id="feedback-section">
        <div class="card-header"><span class="card-icon">📝</span><span class="card-title">今日反馈</span></div>'''
        
        if fb:
            content += f'<div class="feedback-exists"><p>✅ 已记录今日反馈</p>'
            if fb.get('actual_feedback'):
                fb_text = fb['actual_feedback'][:100]
                content += f'<p class="card-sub">你写的: {fb_text}{"..." if len(fb["actual_feedback"])>100 else ""}</p>'
            content += f'<button onclick="editFeedback()" class="btn btn-sm">修改</button></div>'
        
        content += f'''
        <form id="feedback-form" method="post" class="{"hidden" if fb else ""}" onsubmit="return submitFeedback(event)">
        <input type="hidden" name="date" value="{target_date.isoformat()}">
        <input type="hidden" name="prediction_score" value="{s["score"]}">
        <input type="hidden" name="prediction_level" value="{s["level"]}">
        <textarea name="actual_feedback" rows="3" placeholder="今天过得怎么样？记录一下今天实际发生的事…" class="feedback-input"></textarea>
        <div class="feedback-ratings">
        <div class="rating-group"><label>今天整体感受</label>
        <div class="stars" data-name="actual_rating">
        <span class="star" data-value="1" onclick="setRating(this)">☆</span>
        <span class="star" data-value="2" onclick="setRating(this)">☆</span>
        <span class="star" data-value="3" onclick="setRating(this)">☆</span>
        <span class="star" data-value="4" onclick="setRating(this)">☆</span>
        <span class="star" data-value="5" onclick="setRating(this)">☆</span>
        </div><span class="star-hint">轻点星星评分</span></div>
        <div class="rating-group"><label>预测准确度</label>
        <div class="stars" data-name="accuracy_rating">
        <span class="star" data-value="1" onclick="setRating(this)">☆</span>
        <span class="star" data-value="2" onclick="setRating(this)">☆</span>
        <span class="star" data-value="3" onclick="setRating(this)">☆</span>
        <span class="star" data-value="4" onclick="setRating(this)">☆</span>
        <span class="star" data-value="5" onclick="setRating(this)">☆</span>
        </div><span class="star-hint">轻点星星评分</span></div></div>
        <button type="submit" class="btn btn-primary">提交反馈</button>
        </form></div>'''
        
        self._send_html(self._page(content, 'home'))
    
    # ============================================================
    #  月度运势
    # ============================================================
    
    def _serve_monthly(self, year, month):
        reading = interpreter.generate_monthly_reading(year, month)
        
        prev_y, prev_m = (year-1, 12) if month == 1 else (year, month-1)
        next_y, next_m = (year+1, 1) if month == 12 else (year, month+1)
        
        lev_class = LEVEL_CLASSES.get(reading['level'], 'ping')
        
        content = f'''
        <div class="date-nav">
        <a href="/monthly?year={prev_y}&month={prev_m}" class="date-arrow">‹</a>
        <div class="date-center"><h2 class="date-main">{year}年{month}月</h2>
        <span class="date-lunar">{reading['month_pillar']}</span></div>
        <a href="/monthly?year={next_y}&month={next_m}" class="date-arrow">›</a>
        </div>
        
        <div class="score-card" style="background:#f5f0eb">
        <div class="score-circle" style="background:conic-gradient(#5d4037 {reading['avg_score']*3.6}deg,#f0f0f0 {reading['avg_score']*3.6}deg)">
        <div class="score-number">{int(reading['avg_score'])}</div>
        <div class="score-label">月均</div></div>
        <div class="score-info">
        <div class="score-level {lev_class}">{reading['level']}</div>
        <div class="score-pillar">大运: {reading['current_dayun']['name']}</div>
        <div class="score-element">{reading['current_dayun']['age']}岁 · {reading['current_dayun']['start']}-{reading['current_dayun']['end']}</div>
        </div></div>'''
        
        # ---- 月度详细解读 ----
        if 'details' in reading:
            det = reading['details']
            content += f'''
            <div class="card"><div class="card-header"><span class="card-icon">📋</span><span class="card-title">本月总览</span></div>
            <p class="card-text">{det["overview"]}</p></div>
            
            <div class="card"><div class="card-header"><span class="card-icon">💼</span><span class="card-title">事业</span></div>
            <p class="card-text">{det["career"]}</p></div>
            
            <div class="card"><div class="card-header"><span class="card-icon">💰</span><span class="card-title">财运</span></div>
            <p class="card-text">{det["wealth"]}</p></div>
            
            <div class="card"><div class="card-header"><span class="card-icon">🏥</span><span class="card-title">健康</span></div>
            <p class="card-text">{det["health"]}</p></div>
            
            <div class="card"><div class="card-header"><span class="card-icon">👨‍👩‍👧</span><span class="card-title">父母/家庭</span></div>
            <p class="card-text">{det["family"]}</p></div>
            
            <div class="card"><div class="card-header"><span class="card-icon">💕</span><span class="card-title">感情/姻缘</span></div>
            <p class="card-text">{det["love"]}</p></div>'''
            
            if det.get('warnings'):
                for w in det['warnings']:
                    icon = '⚠' if '⚠' in w else '✓' if '✓' in w else '△'
                    bg = '#fff8e1' if '⚠' in w else '#f5f0eb'
                    content += f'<div class="card" style="background:{bg}"><p class="card-text">{w}</p></div>'
        
        # ---- 工作建议 ----
        if 'work_advice' in reading and reading['work_advice']:
            content += '<div class="card card-reminder"><div class="card-header"><span class="card-icon">💡</span><span class="card-title">上班族建议</span></div>'
            for a in reading['work_advice']:
                content += f'<p class="card-text">{a}</p>'
            content += '</div>'
        
        if reading['key_dates']['good_days']:
            content += '<div class="card"><div class="card-header"><span class="card-icon">✅</span><span class="card-title">吉日推荐</span></div><div class="date-list">'
            for d in reading['key_dates']['good_days']:
                content += f'<a href="/date/{d["date"].strftime("%Y/%m/%d")}" class="date-item date-good"><span class="date-day">{d["date"].strftime("%m月%d日")}</span><span class="date-pillar">{d["pillar"]}</span><span class="date-score">{d["score"]}</span></a>'
            content += '</div></div>'
        
        if reading['key_dates']['bad_days']:
            content += '<div class="card"><div class="card-header"><span class="card-icon">⚠️</span><span class="card-title">需谨慎日</span></div><div class="date-list">'
            for d in reading['key_dates']['bad_days']:
                content += f'<a href="/date/{d["date"].strftime("%Y/%m/%d")}" class="date-item date-bad"><span class="date-day">{d["date"].strftime("%m月%d日")}</span><span class="date-pillar">{d["pillar"]}</span><span class="date-score">{d["score"]}</span></a>'
            content += '</div></div>'
        
        content += '<div class="card"><div class="card-header"><span class="card-icon">📅</span><span class="card-title">日运日历</span></div><div class="mini-calendar">'
        for d in reading['key_dates']['all']:
            bg = '#fff8e1' if d['score'] >= 70 else '#f5f0eb' if d['score'] >= 50 else '#efebe9' if d['score'] >= 35 else '#e0e0e0'
            content += f'<a href="/date/{d["date"].strftime("%Y/%m/%d")}" class="mini-day" style="background:{bg}"><span class="mini-day-num">{d["date"].day}</span><span class="mini-day-score">{d["score"]}</span></a>'
        content += '</div></div>'
        
        self._send_html(self._page(content, 'monthly'))
    
    # ============================================================
    #  年度运势
    # ============================================================
    
    def _serve_yearly(self, year):
        reading = interpreter.generate_yearly_reading(year)
        lev_class = LEVEL_CLASSES.get(reading['level'], 'ping')
        
        content = f'''
        <div class="date-nav">
        <a href="/yearly?year={year-1}" class="date-arrow">‹</a>
        <div class="date-center"><h2 class="date-main">{year}年</h2>
        <span class="date-lunar">{reading['year_pillar']} · {reading['year_ten_god']}</span></div>
        <a href="/yearly?year={year+1}" class="date-arrow">›</a>
        </div>
        
        <div class="score-card" style="background:#f5f0eb">
        <div class="score-circle" style="background:conic-gradient(#5d4037 {reading['avg_score']*3.6}deg,#f0f0f0 {reading['avg_score']*3.6}deg)">
        <div class="score-number">{int(reading['avg_score'])}</div>
        <div class="score-label">年均</div></div>
        <div class="score-info">
        <div class="score-level {lev_class}">{reading['level']}</div>
        <div class="score-pillar">{reading['year_pillar']} · 年干为{reading['year_ten_god']}</div>
        <div class="score-element">{"喜用神" if reading.get("is_favorable_year") else "忌神"}之年</div>
        </div></div>'''
        
        kw = reading.get('keywords', {})
        if kw:
            content += '<div class="card card-highlight"><div class="card-header"><span class="card-icon">🔮</span><span class="card-title">年度解读</span></div>'
            if isinstance(kw, dict) and 'keywords' in kw:
                content += '<div class="keyword-row">'
                for k in kw['keywords']:
                    content += f'<span class="tag" style="background:#5d4037;color:#fff;font-weight:600;padding:4px 14px;border-radius:16px;font-size:14px">{k}</span>'
                content += '</div>'
                if 'message' in kw:
                    content += f'<p class="card-text">{kw["message"]}</p>'
            content += '</div>'
        
        # ---- 年度详细解读 ----
        if 'details' in reading:
            det = reading['details']
            content += f'''
            <div class="card"><div class="card-header"><span class="card-icon">📋</span><span class="card-title">年度总览</span></div>
            <p class="card-text">{det["overview"]}</p></div>
            
            <div class="card"><div class="card-header"><span class="card-icon">💼</span><span class="card-title">事业</span></div>
            <p class="card-text">{det["career"]}</p></div>
            
            <div class="card"><div class="card-header"><span class="card-icon">💰</span><span class="card-title">财运</span></div>
            <p class="card-text">{det["wealth"]}</p></div>
            
            <div class="card"><div class="card-header"><span class="card-icon">🏥</span><span class="card-title">健康</span></div>
            <p class="card-text">{det["health"]}</p></div>
            
            <div class="card"><div class="card-header"><span class="card-icon">👨‍👩‍👧</span><span class="card-title">父母/家庭</span></div>
            <p class="card-text">{det["family"]}</p></div>
            
            <div class="card"><div class="card-header"><span class="card-icon">💕</span><span class="card-title">感情/姻缘</span></div>
            <p class="card-text">{det["love"]}</p></div>'''
            if det.get('warnings'):
                for w in det['warnings']:
                    content += f'<div class="card card-highlight"><p class="card-text">{w}</p></div>'
        
        du = reading['current_dayun']
        content += f'''
        <div class="card"><div class="card-header"><span class="card-icon">🔄</span><span class="card-title">大运 · {du['name']}</span>
        <span class="card-badge">{du['age']}岁</span></div>
        <p class="card-text">起止: {du['start']} - {du['end']}</p></div>
        
        <div class="card"><div class="card-header"><span class="card-icon">📈</span><span class="card-title">月度走势</span></div>
        <div class="month-chart">'''
        for m in reading['monthly_overview']:
            bg = '#bf8f00' if m['score'] >= 70 else '#8d6e00' if m['score'] >= 50 else '#5d4037'
            content += f'<div class="month-bar-wrapper"><div class="month-bar" style="height:{m["score"]}px;background:{bg}"></div><span class="month-label">{m["month"]}月</span><span class="month-score">{int(m["score"])}</span></div>'
        content += '</div></div>'
        
        content += '<div class="card"><div class="card-header"><span class="card-icon">📋</span><span class="card-title">月运详情</span></div><div class="month-detail-list">'
        for m in reading['monthly_overview']:
            color = '#8d6e00' if m['score'] >= 70 else '#5d4037' if m['score'] >= 50 else '#4e342e'
            content += f'<a href="/monthly?year={reading["year"]}&month={m["month"]}" class="month-detail-item"><span class="month-detail-name">{m["month"]}月</span><span class="month-detail-pillar">{m["pillar"]}</span><span class="month-detail-level" style="color:{color}">{m["level"]}</span><span class="month-detail-score">{int(m["score"])}分</span></a>'
        content += '</div></div>'
        
        content += '<div class="card"><div class="card-header"><span class="card-icon">📚</span><span class="card-title">切换年份</span></div><div class="mini-calendar" style="grid-template-columns:repeat(4,1fr)">'
        for y in range(year-3, year+4):
            bg = '#5d4037' if y == year else '#f5f5f5'
            color = '#fff' if y == year else '#555'
            content += f'<a href="/yearly?year={y}" class="mini-day" style="background:{bg};color:{color};padding:12px;font-weight:{"700" if y==year else "400"}">{y}年</a>'
        content += '</div></div>'
        
        self._send_html(self._page(content, 'yearly'))
    
    # ============================================================
    #  日记
    # ============================================================
    
    def _serve_diary(self):
        today = date.today()
        diaries = get_diary_entries(30)
        
        content = f'''
        <h2 class="page-title">📝 每日日记</h2>
        <p class="page-subtitle">记录今天发生了什么，帮助命理算法更精准 💡 可以使用手机语音输入哦</p>
        
        <div class="card"><div class="card-header"><span class="card-icon">✏️</span><span class="card-title">今日记录 · {today.strftime("%Y年%m月%d日")}</span></div>
        <form id="diary-form" onsubmit="return submitDiary(event)">
        <div style="display:flex;gap:8px;margin-bottom:8px">
        <textarea name="content" rows="5" class="diary-input" id="diary-input" placeholder="今天发生了什么？有什么开心的事、困扰的事、或者有趣的事？"></textarea>
        <button type="button" id="voice-btn" onclick="toggleVoiceInput()" style="flex-shrink:0;width:48px;height:48px;border-radius:50%;border:2px solid #e0e0e0;background:#fff;font-size:22px;cursor:pointer;display:flex;align-items:center;justify-content:center" title="语音输入（支持手机浏览器语音键盘）">🎤</button>
        </div>
        <div id="voice-status" style="font-size:13px;color:#888;display:none;margin-bottom:8px">🎙️ 正在听… 说完后点击停止</div>
        <div class="diary-extras">
        <div class="diary-mood"><label>心情：</label>
        <select name="mood" class="mood-select">
        <option value="5">😄 很好</option><option value="4">🙂 不错</option>
        <option value="3">😐 一般</option><option value="2">😔 不好</option>
        <option value="1">😢 很差</option></select></div>
        <div class="diary-category"><label>类别：</label>
        <select name="category" class="category-select">
        <option value="日常">日常</option><option value="工作">工作</option>
        <option value="感情">感情</option><option value="家庭">家庭</option>
        <option value="健康">健康</option><option value="社交">社交</option>
        <option value="其他">其他</option></select></div></div>
        <button type="submit" class="btn btn-primary">💾 保存日记</button>
        </form></div>
        
        <div class="card"><div class="card-header"><span class="card-icon">📖</span><span class="card-title">最近记录</span></div>'''
        
        if diaries:
            content += '<div class="diary-list">'
            for entry in diaries:
                mood_emoji = {'5':'😄','4':'🙂','3':'😐','2':'😔','1':'😢'}
                content += f'<div class="diary-item"><div class="diary-item-header"><span class="diary-date">{entry["date"]}</span><span class="diary-time">{entry["entry_time"]}</span><span class="diary-cat-badge">{entry.get("category","日常")}</span></div><p class="diary-content">{entry["content"][:200]}{"…" if len(entry["content"])>200 else ""}</p></div>'
            content += '</div>'
        else:
            content += '<p class="card-text card-sub">还没有日记记录，开始记录今天吧！</p>'
        
        content += '</div>'
        self._send_html(self._page(content, 'diary'))
    
    # ============================================================
    #  历史记录
    # ============================================================
    
    def _serve_history(self):
        feedbacks = get_recent_feedback(90)
        stats = get_feedback_accuracy_stats()
        
        content = f'''
        <h2 class="page-title">📊 反馈记录</h2>
        <p class="page-subtitle">你的反馈越多，我的预测越准</p>
        
        <div class="stats-row">
        <div class="stat-card"><div class="stat-number">{stats["total"]}</div><div class="stat-label">累计反馈</div></div>
        <div class="stat-card"><div class="stat-number">{stats["avg_accuracy"]}</div><div class="stat-label">平均准确率</div></div>
        <div class="stat-card"><div class="stat-number">{stats["avg_actual"]}</div><div class="stat-label">平均感受</div></div>
        </div>
        
        <div class="card"><div class="card-header"><span class="card-icon">📋</span><span class="card-title">反馈历史</span></div>'''
        
        if feedbacks:
            content += '<div class="feedback-list">'
            for fb in feedbacks:
                lev_bg = {'大吉':'#c8e6c9','吉':'#dcedc8','平':'#fff9c4','不佳':'#ffe0b2','谨慎':'#ffcdd2'}.get(fb.get('prediction_level','平'), '#fff9c4')
                content += f'<div class="feedback-item"><div class="fb-header"><a href="/date/{fb["date"]}" class="fb-date">{fb["date"]}</a><span class="fb-level" style="background:{lev_bg}">{fb.get("prediction_level","")}</span><span class="fb-score">{fb.get("prediction_score","")}分</span></div>'
                if fb.get('actual_feedback'):
                    content += f'<p class="fb-content">{fb["actual_feedback"][:200]}{"…" if len(fb["actual_feedback"])>200 else ""}</p>'
                content += '<div class="fb-ratings">'
                if fb.get('actual_rating'):
                    content += f'<span>感受: {"★"*fb["actual_rating"]}{"☆"*(5-fb["actual_rating"])}</span>'
                if fb.get('accuracy_rating'):
                    content += f'<span>准确度: {"★"*fb["accuracy_rating"]}{"☆"*(5-fb["accuracy_rating"])}</span>'
                content += '</div></div>'
            content += '</div>'
        else:
            content += '<p class="card-text card-sub">还没有反馈记录。每天看完运势后，记得回来反馈一下哦！</p>'
        
        content += '</div>'
        content += '''
        <div class="card card-reminder"><div class="card-header"><span class="card-icon">💡</span><span class="card-title">使用流程</span></div>
        <ol style="padding-left:20px">
        <li style="font-size:14px;color:#555;margin-bottom:8px">🌅 早上打开「今日」页面看运势</li>
        <li style="font-size:14px;color:#555;margin-bottom:8px">📝 晚上在「日记」页面记录今天发生的事</li>
        <li style="font-size:14px;color:#555;margin-bottom:8px">⭐ 在运势页面反馈「今天的预测准不准」</li>
        <li style="font-size:14px;color:#555;margin-bottom:8px">📊 反馈越多，算法校准越精准</li>
        </ol></div>'''
        
        self._send_html(self._page(content, 'history'))
    
    def _serve_api(self, path, params):
        self._send_json({'error': 'not found'}, 404)
    
    def _serve_css(self):
        pass  # CSS is inline in HTML

    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]} {args[1]} {args[2]}")


# ============================================================
#  启动
# ============================================================

# ============================================================
#  WSGI 兼容层 (用于 PythonAnywhere 等云平台)
# ============================================================

def app(environ, start_response):
    """WSGI application entry point"""
    # 捕获 BaziHandler 的输出
    from io import BytesIO
    import sys
    
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET')
    
    # 创建模拟请求
    class FakeSocket:
        def __init__(self):
            self.data = b''
            self.headers = {}
    
    # 直接使用 do_GET/do_POST 逻辑
    handler = BaziHandler(None, ('0.0.0.0', 0), None)
    
    # 重写发送方法
    output = []
    status_code = '200 OK'
    response_headers = []
    
    def fake_send_response(code):
        nonlocal status_code
        status_code = f'{code} OK'
    
    def fake_send_header(key, value):
        response_headers.append((key, value))
    
    def fake_end_headers():
        pass
    
    def fake_send(data):
        if isinstance(data, str):
            output.append(data.encode('utf-8'))
        else:
            output.append(data)
    
    handler.send_response = fake_send_response
    handler.send_header = fake_send_header
    handler.end_headers = fake_end_headers
    handler.wfile = FakeSocket()
    
    def fake_write(data):
        if isinstance(data, str):
            output.append(data.encode('utf-8'))
        else:
            output.append(data)
    
    handler.wfile.write = fake_write
    
    # 设置请求信息
    handler.path = path
    handler.headers = {}
    handler.command = method
    
    # 从 environ 获取 headers
    for key, value in environ.items():
        if key.startswith('HTTP_'):
            header_name = key[5:].replace('_', '-').title()
            handler.headers[header_name] = value
        elif key in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            handler.headers[key.replace('_', '-').title()] = value
    
    # 处理请求
    try:
        if method == 'GET':
            handler.do_GET()
        elif method == 'POST':
            # 读取 body
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            body = environ['wsgi.input'].read(content_length) if content_length > 0 else b''
            handler.rfile = BytesIO(body) if body else BytesIO(b'{}')
            handler.do_POST()
    except Exception as e:
        output = [f'Error: {e}'.encode('utf-8')]
    
    # 返回 WSGI 响应
    output_data = b''.join(output) if output else b'OK'
    start_response(status_code, response_headers)
    return [output_data]


if __name__ == '__main__':
    init_db()
    
    print(f'''
    ╔══════════════════════════════════════════╗
    ║     🌟 Karen 专属命理工具  v1.0         ║
    ║                                          ║
    ║  辛金日主 | 身弱 | 喜土金 | 忌木火      ║
    ║  当前大运: 丙戌 → 即将换入乙酉 🔥      ║
    ║                                          ║
    ║  📱 电脑访问: http://127.0.0.1:{PORT}      ║
    ║  📱 手机访问: http://你电脑的IP:{PORT} ║
    ║                                          ║
    ║  提示: 如需手机访问, 先确认在同一WiFi   ║
    ╚══════════════════════════════════════════╝
    ''')
    
    server = HTTPServer((HOST, PORT), BaziHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n👋 服务已停止')
        server.server_close()
