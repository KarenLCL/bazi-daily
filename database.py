"""
数据库模块 - 存储每日日记/反馈
使用SQLite，轻量级无需额外安装
"""

import sqlite3
import os
from datetime import date, datetime
from typing import List, Dict, Optional


DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'bazi_daily.db')


def get_connection():
    """获取数据库连接"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            prediction_score INTEGER,
            prediction_level TEXT,
            actual_feedback TEXT,
            actual_rating INTEGER,
            accuracy_rating INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diary_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            entry_time TEXT NOT NULL,
            content TEXT NOT NULL,
            mood INTEGER,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracked_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_name TEXT NOT NULL,
            description TEXT,
            trigger_conditions TEXT,
            accuracy INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT DEFAULT '其他',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()


def save_daily_feedback(feedback_data: Dict) -> bool:
    """保存每日反馈"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO daily_feedback 
            (date, prediction_score, prediction_level, actual_feedback, actual_rating, accuracy_rating)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                prediction_score = excluded.prediction_score,
                prediction_level = excluded.prediction_level,
                actual_feedback = excluded.actual_feedback,
                actual_rating = excluded.actual_rating,
                accuracy_rating = excluded.accuracy_rating,
                updated_at = CURRENT_TIMESTAMP
        ''', (
            feedback_data.get('date'),
            feedback_data.get('prediction_score'),
            feedback_data.get('prediction_level'),
            feedback_data.get('actual_feedback'),
            feedback_data.get('actual_rating'),
            feedback_data.get('accuracy_rating'),
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"保存反馈失败: {e}")
        return False
    finally:
        conn.close()


def save_diary_entry(entry: Dict) -> bool:
    """保存日记条目"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO diary_entries (date, entry_time, content, mood, category)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            entry.get('date'),
            entry.get('entry_time'),
            entry.get('content'),
            entry.get('mood'),
            entry.get('category'),
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"保存日记失败: {e}")
        return False
    finally:
        conn.close()


def get_feedback_by_date(target_date: str) -> Optional[Dict]:
    """获取指定日期的反馈"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM daily_feedback WHERE date = ?', (target_date,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def get_recent_feedback(limit: int = 30) -> List[Dict]:
    """获取最近的反馈记录"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM daily_feedback 
        ORDER BY date DESC 
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_diary_entries(limit: int = 30) -> List[Dict]:
    """获取最近的日记"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM diary_entries 
        ORDER BY date DESC, id DESC 
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_feedback_accuracy_stats() -> Dict:
    """获取反馈准确率统计"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            AVG(accuracy_rating) as avg_accuracy,
            AVG(actual_rating) as avg_actual
        FROM daily_feedback 
        WHERE accuracy_rating IS NOT NULL
    ''')
    
    stats = cursor.fetchone()
    conn.close()
    
    if stats and stats['total'] > 0:
        return {
            'total': stats['total'],
            'avg_accuracy': round(stats['avg_accuracy'], 1) if stats['avg_accuracy'] else 0,
            'avg_actual': round(stats['avg_actual'], 1) if stats['avg_actual'] else 0,
        }
    return {'total': 0, 'avg_accuracy': 0, 'avg_actual': 0}


def get_feedback_by_month(year: int, month: int) -> List[Dict]:
    """获取某月的反馈"""
    conn = get_connection()
    cursor = conn.cursor()
    
    month_str = f"{year:04d}-{month:02d}%"
    cursor.execute('''
        SELECT * FROM daily_feedback 
        WHERE date LIKE ?
        ORDER BY date ASC
    ''', (month_str,))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
