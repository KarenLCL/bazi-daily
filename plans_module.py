"""
计划/特殊事件模块
用户可以添加特殊计划或变化，在每日运势中显示
"""

from database import get_connection
from datetime import date, datetime
from typing import List, Dict, Optional


def add_plan(plan_data: Dict) -> bool:
    """添加计划"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO plans (date, title, description, category)
            VALUES (?, ?, ?, ?)
        ''', (
            plan_data.get('date'),
            plan_data.get('title'),
            plan_data.get('description', ''),
            plan_data.get('category', '其他'),
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"添加计划失败: {e}")
        return False
    finally:
        conn.close()


def get_plans_by_date(target_date: str) -> List[Dict]:
    """获取指定日期的计划"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM plans WHERE date = ? ORDER BY id', (target_date,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_upcoming_plans(limit: int = 10) -> List[Dict]:
    """获取即将到来的计划"""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()
    cursor.execute('''
        SELECT * FROM plans 
        WHERE date >= ? 
        ORDER BY date ASC 
        LIMIT ?
    ''', (today, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_recent_plans(limit: int = 20) -> List[Dict]:
    """获取最近和即将的计划"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM plans 
        ORDER BY date DESC 
        LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_plan(plan_id: int) -> bool:
    """删除计划"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM plans WHERE id = ?', (plan_id,))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()
