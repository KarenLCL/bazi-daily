"""
专属命理工具 - Flask Web 应用
为 Karen 定制的每日/每月/每年命理解读
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import date, datetime
import json

from bazi_engine import (
    HEAVENLY_STEMS, EARTHLY_BRANCHES,
    get_day_stem_branch, calculate_daily_bazi,
    calculate_daily_score, compare_with_birth_chart,
    get_bazi_pillar_name, get_five_element_from_stem,
    get_five_element_from_branch, get_ten_god,
)
from user_profile import PROFILE, BIRTH_CHART, get_current_dayun
from interpreter import PersonalizedInterpreter
from database import (
    init_db, save_daily_feedback, save_diary_entry,
    get_feedback_by_date, get_recent_feedback,
    get_diary_entries, get_feedback_accuracy_stats,
    get_feedback_by_month
)

app = Flask(__name__)
interpreter = PersonalizedInterpreter()


@app.route('/')
def index():
    """首页 - 今日运势"""
    today = date.today()
    reading = interpreter.generate_daily_reading(today)
    
    # 检查今天是否已有反馈
    feedback = get_feedback_by_date(today.isoformat())
    has_feedback = feedback is not None
    
    return render_template('index.html', 
                         reading=reading,
                         today=today,
                         has_feedback=has_feedback,
                         feedback=feedback)


@app.route('/date/<year>/<month>/<day>')
def by_date(year, month, day):
    """按日期查看运势"""
    try:
        target_date = date(int(year), int(month), int(day))
    except ValueError:
        return redirect(url_for('index'))
    
    reading = interpreter.generate_daily_reading(target_date)
    feedback = get_feedback_by_date(target_date.isoformat())
    
    return render_template('index.html',
                         reading=reading,
                         today=target_date,
                         has_feedback=feedback is not None,
                         feedback=feedback)


@app.route('/monthly')
def monthly_view():
    """月度运势"""
    today = date.today()
    year = request.args.get('year', today.year, type=int)
    month = request.args.get('month', today.month, type=int)
    
    if month < 1 or month > 12:
        month = today.month
    
    reading = interpreter.generate_monthly_reading(year, month)
    
    return render_template('monthly.html',
                         reading=reading,
                         current_year=year,
                         current_month=month,
                         today=today)


@app.route('/yearly')
def yearly_view():
    """年度运势"""
    today = date.today()
    year = request.args.get('year', today.year, type=int)
    
    reading = interpreter.generate_yearly_reading(year)
    
    return render_template('yearly.html',
                         reading=reading,
                         current_year=year,
                         today=today)


@app.route('/history')
def history_view():
    """历史反馈和日记"""
    feedbacks = get_recent_feedback(90)
    diaries = get_diary_entries(30)
    stats = get_feedback_accuracy_stats()
    
    return render_template('history.html',
                         feedbacks=feedbacks,
                         diaries=diaries,
                         stats=stats)


@app.route('/diary')
def diary_view():
    """日记页面"""
    today = date.today()
    today_feedback = get_feedback_by_date(today.isoformat())
    recent_feedbacks = get_recent_feedback(30)
    diaries = get_diary_entries(30)
    
    return render_template('diary.html',
                         today=today,
                         today_feedback=today_feedback,
                         recent_feedbacks=recent_feedbacks,
                         diaries=diaries)


# ============ API 接口 ============

@app.route('/api/daily/<year>/<month>/<day>')
def api_daily(year, month, day):
    """API: 获取每日运势"""
    target_date = date(int(year), int(month), int(day))
    reading = interpreter.generate_daily_reading(target_date)
    
    # 转为可序列化的格式
    result = _serialize_reading(reading)
    return jsonify(result)


@app.route('/api/monthly/<int:year>/<int:month>')
def api_monthly(year, month):
    """API: 获取月度运势"""
    reading = interpreter.generate_monthly_reading(year, month)
    return jsonify(_serialize_monthly(reading))


@app.route('/api/yearly/<int:year>')
def api_yearly(year):
    """API: 获取年度运势"""
    reading = interpreter.generate_yearly_reading(year)
    return jsonify(_serialize_yearly(reading))


@app.route('/api/feedback', methods=['POST'])
def api_feedback():
    """API: 提交当日反馈"""
    data = request.json
    if not data:
        return jsonify({"error": "无效的请求数据"}), 400
    
    feedback_data = {
        'date': data.get('date', date.today().isoformat()),
        'prediction_score': data.get('prediction_score'),
        'prediction_level': data.get('prediction_level'),
        'actual_feedback': data.get('actual_feedback', ''),
        'actual_rating': data.get('actual_rating'),
        'accuracy_rating': data.get('accuracy_rating'),
    }
    
    success = save_daily_feedback(feedback_data)
    if success:
        return jsonify({"status": "ok", "message": "反馈已保存"})
    return jsonify({"error": "保存失败"}), 500


@app.route('/api/diary', methods=['POST'])
def api_diary():
    """API: 提交日记"""
    data = request.json
    if not data or not data.get('content'):
        return jsonify({"error": "请输入日记内容"}), 400
    
    entry = {
        'date': data.get('date', date.today().isoformat()),
        'entry_time': datetime.now().strftime('%H:%M'),
        'content': data.get('content', ''),
        'mood': data.get('mood'),
        'category': data.get('category', '日常'),
    }
    
    success = save_diary_entry(entry)
    if success:
        return jsonify({"status": "ok", "message": "日记已保存"})
    return jsonify({"error": "保存失败"}), 500


@app.route('/api/today')
def api_today():
    """API: 获取今日运势（简约版，适合手机）"""
    today = date.today()
    reading = interpreter.generate_daily_reading(today)
    result = _serialize_reading_simple(reading)
    return jsonify(result)


# ============ 序列化辅助函数 ============

def _serialize_reading(reading):
    """完整序列化每日解读"""
    return {
        "date": reading["date"].isoformat(),
        "daily_bazi": {
            "year": reading["daily_bazi"]["year"]["name"],
            "month": reading["daily_bazi"]["month"]["name"],
            "day": reading["daily_bazi"]["day"]["name"],
            "hour": reading["daily_bazi"]["hour"]["name"],
            "nayin": reading["daily_bazi"]["day"]["nayin"],
        },
        "score": {
            "score": reading["score"]["score"],
            "level": reading["score"]["level"],
        },
        "overview": reading["interpretation"]["overview"],
        "career": reading["interpretation"]["career"],
        "relationship": reading["interpretation"]["relationship"],
        "health": reading["interpretation"]["health"],
        "family": reading["interpretation"]["family"],
        "advice": reading["interpretation"]["advice"],
        "reminders": reading["interpretation"]["reminders"],
        "hour_reading": reading["hour_reading"],
        "current_dayun": reading["current_dayun"],
    }


def _serialize_reading_simple(reading):
    """简约版序列化（适合手机端加载）"""
    return {
        "date": reading["date"].isoformat(),
        "score": reading["score"]["score"],
        "level": reading["score"]["level"],
        "summary": reading["interpretation"]["overview"]["summary"],
        "career": reading["interpretation"]["career"]["ten_god_reading"],
        "relationship": reading["interpretation"]["relationship"]["ten_god_reading"],
        "health_tips": reading["interpretation"]["health"]["tips"],
        "family": reading["interpretation"]["family"]["notes"],
        "favorable": reading["interpretation"]["advice"]["favorable"][:3],
        "unfavorable": reading["interpretation"]["advice"]["unfavorable"][:3],
        "reminders": reading["interpretation"]["reminders"],
        "hour": reading["hour_reading"]["ten_god_reading"],
    }


def _serialize_monthly(reading):
    """序列化月度解读"""
    return {
        "year": reading["year"],
        "month": reading["month"],
        "month_pillar": reading["month_pillar"],
        "avg_score": reading["avg_score"],
        "level": reading["level"],
        "key_dates": {
            "good": [{"date": d["date"].isoformat(), "score": d["score"], "pillar": d["pillar"]} 
                    for d in reading["key_dates"]["good_days"]],
            "bad": [{"date": d["date"].isoformat(), "score": d["score"], "pillar": d["pillar"]} 
                   for d in reading["key_dates"]["bad_days"]],
        }
    }


def _serialize_yearly(reading):
    """序列化年度解读"""
    return {
        "year": reading["year"],
        "year_pillar": reading["year_pillar"],
        "year_ten_god": reading["year_ten_god"],
        "avg_score": reading["avg_score"],
        "level": reading["level"],
        "keywords": reading["keywords"],
        "monthly_overview": [{
            "month": m["month"],
            "score": m["score"],
            "level": m["level"],
            "pillar": m["pillar"],
        } for m in reading["monthly_overview"]],
    }


# ============ 启动 ============

if __name__ == '__main__':
    # 初始化数据库
    init_db()
    
    print("""
    ╔══════════════════════════════════════════╗
    ║     🌟 Karen 专属命理工具  v1.0         ║
    ║                                          ║
    ║  辛金日主 | 身弱 | 喜土金 | 忌木火      ║
    ║  当前大运: 丙戌 → 即将换入乙酉 🔥      ║
    ║                                          ║
    ║  手机访问: http://YOUR_IP:5000          ║
    ╚══════════════════════════════════════════╝
    """)
    
    # 监听所有网络接口，允许局域网访问
    app.run(host='0.0.0.0', port=5000, debug=True)
