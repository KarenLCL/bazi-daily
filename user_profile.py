"""
用户个人档案模块
基于已验证的命盘数据和人生经历校准
"""

from datetime import date, datetime
from typing import Dict

# ============ 出生信息 ============
BIRTH_INFO = {
    "name": "Karen",
    "birth_date": date(1986, 2, 6),
    "birth_time": "15:10",
    "birth_place": "江苏南京",
    "gender": "女",
    "true_solar_time": "14:51",  # 真太阳时校准
}

# ============ 八字四柱 (已通过真太阳时校准验证) ============
BIRTH_CHART = {
    "year": {"stem": 2, "branch": 2, "name": "丙寅"},      # 正官
    "month": {"stem": 6, "branch": 2, "name": "庚寅"},     # 劫财
    "day": {"stem": 7, "branch": 5, "name": "辛巳"},       # 元女 (日主)
    "hour": {"stem": 1, "branch": 7, "name": "乙未"},      # 偏财
}

# ============ 命局判断 (已通过人生大事交叉验证) ============
# 验证事件清单:
# ✅ 2000年中考差3分(庚辰) - 土金年但子辰合水泄气
# ✅ 2002年奶奶去世(壬午) - 壬丙冲祖上宫
# ✅ 2004年高考失利(甲申) - 申冲寅根基动摇
# ✅ 2015年分手(乙未) - 时柱伏吟
# ✅ 2018年父亲肺癌(戊戌) - 戌未刑,火库克金
# ✅ 2019-2020年收入巅峰(己亥庚子) - 土金水用神到位
# ✅ 2022年感情诈骗(壬寅) - 三寅聚齐偏财忌神
# ✅ 2023年被辞退(癸卯) - 木旺至极官杀克身
# ✅ 2023-2024年NPD纠缠(癸卯甲辰)

PROFILE = {
    # === 日主 ===
    "day_master": {
        "stem": 7,              # 辛
        "element": "金",
        "yinyang": "阴",
        "strength": "身弱",      # 春金生于寅月，木旺火相，金处绝地
    },
    
    # === 用神忌神 (已完全验证) ===
    "favorite_elements": ["土", "金"],      # ✅ 已验证
    "unfavorable_elements": ["木", "火"],   # ✅ 已验证
    "neutral_elements": ["水"],             # 利弊参半
    
    "favorite_stems": [4, 5, 6, 7],        # 戊己庚辛
    "unfavorable_stems": [0, 1, 2, 3],     # 甲乙丙丁
    
    "favorite_branches": {
        "earth": [1, 4, 7, 10],   # 丑辰未戌 (土)
        "metal": [8, 9],          # 申酉 (金)
    },
    "unfavorable_branches": {
        "wood": [2, 3, 11],       # 寅卯亥 (木)
        "fire": [5, 6],           # 巳午 (火)
    },
    
    # === 十神 ===
    "ten_gods": {
        "year_stem": "正官",     # 丙火
        "month_stem": "劫财",    # 庚金
        "day_stem": "元女",      # 辛金
        "hour_stem": "偏财",     # 乙木
    },
    
    # === 神煞 ===
    "gods": {
        "auspicious": ["天乙贵人", "太极贵人", "福星贵人", "学堂", 
                       "国印贵人", "天厨贵人", "月德合", "天喜", "金舆"],
        "ominous": ["孤辰", "亡神", "元辰", "十恶大败"],
    },
    
    # === 性格特征 (已验证) ===
    "personality": {
        "type": "孤辰型享受独处",
        "traits": [
            "独处充电，社交耗电 - 这是正常的，不是缺陷",
            "外表温和有礼，内心敏感多思",
            "思维灵活，适合深度分析和创作",
            "对规则和秩序有天然追求（正官格）",
            "有贵人的命，但需要主动一些",
        ],
        "needs": [
            "需要大量独处时间恢复能量",
            "需要结构化的工作环境（大平台+制度）",
            "需要少量但高质量的人际关系",
            "需要有意义感和深度的工作内容",
        ]
    },
    
    # === 大运 ===
    "dayun": [
        {"name": "己丑", "stem": 5, "branch": 1, "start": 1986, "end": 1996, "age": "1-10"},
        {"name": "戊子", "stem": 4, "branch": 0, "start": 1996, "end": 2006, "age": "11-20"},
        {"name": "丁亥", "stem": 3, "branch": 11, "start": 2006, "end": 2016, "age": "21-30"},
        {"name": "丙戌", "stem": 2, "branch": 10, "start": 2016, "end": 2027, "age": "31-40"},   # 实际到2026年10月
        {"name": "乙酉", "stem": 1, "branch": 9, "start": 2027, "end": 2036, "age": "41-50"},   # 🔥 黄金大运 (10月后切换)
        {"name": "甲申", "stem": 0, "branch": 8, "start": 2036, "end": 2046, "age": "51-60"},
        {"name": "癸未", "stem": 9, "branch": 7, "start": 2046, "end": 2056, "age": "61-70"},
        {"name": "壬午", "stem": 8, "branch": 6, "start": 2056, "end": 2066, "age": "71-80"},
    ],
    "current_dayun_index": 3,  # 目前仍在丙戌运 (索引3)
    
    # === 已验证的人生大事 (用于校准) ===
    "verified_events": [
        {"year": 2000, "event": "中考差3分理想高中，交钱入学", "analysis": "庚辰年，子辰合水泄金气"},
        {"year": 2002, "event": "奶奶去世（2月19日壬午年壬寅月）", "analysis": "壬丙冲年干祖上宫"},
        {"year": 2004, "event": "高考失利，去烂大学", "analysis": "申冲寅根基动摇，申巳合水"},
        {"year": 2015, "event": "结束5年恋爱", "analysis": "乙未时柱伏吟"},
        {"year": 2018, "event": "父亲肺癌重病", "analysis": "戊戌年双戌刑未，火库克金"},
        {"year": 2019, "event": "收入开始变好", "analysis": "己亥年偏印生身"},
        {"year": 2020, "event": "收入巅峰（18-19期权兑现）", "analysis": "庚子年劫财帮身最强吉年"},
        {"year": 2022, "event": "情感诈骗（伪装富二代）", "analysis": "壬寅年三寅聚齐偏财忌神"},
        {"year": 2023, "event": "被辞退领大礼包", "analysis": "癸卯年木旺极官杀克身"},
        {"year": 2024, "event": "NPD纠缠，消耗金钱精力", "analysis": "甲辰年正财忌神"},
    ],
}

# ============ 父母信息 ============
PARENTS_INFO = {
    "father": {
        "birth_year": 1948,
        "birth_date": date(1948, 1, 19),
        "birth_time": "不详",
        "bazi": {
            "year": {"stem": 3, "branch": 11, "name": "丁亥"},
            "month": {"stem": 9, "branch": 1, "name": "癸丑"},
            "day": {"stem": 6, "branch": 6, "name": "庚午"},
            "hour": {"stem": -1, "branch": -1, "name": "不详"},
        },
        "health_issues": ["肺癌(2018)", "AD/记忆衰退迹象"],
        "key_years": [2027, 2029],  # 需关注的年份
    },
    "mother": {
        "birth_year": 1947,
        "birth_date": date(1947, 2, 22),
        "birth_time": "子时",
        "bazi": {
            "year": {"stem": 3, "branch": 11, "name": "丁亥"},
            "month": {"stem": 8, "branch": 2, "name": "壬寅"},
            "day": {"stem": 5, "branch": 11, "name": "己亥"},
            "hour": {"stem": 0, "branch": 0, "name": "甲子"},
        },
        "health_issues": ["脾胃虚弱", "湿气重"],
        "key_years": [2034],  # 三寅克土
    },
}


def get_current_dayun(target_date: date = None) -> Dict:
    """获取当前大运"""
    if target_date is None:
        target_date = date.today()
    
    # 大运精确计算：丙戌运到2026年10月结束
    # 2026年10月前 = 丙戌运(索引3)，2026年10月起 = 乙酉运(索引4)
    if target_date < date(2026, 10, 1):
        return {**PROFILE["dayun"][3], "index": 3}
    else:
        return {**PROFILE["dayun"][4], "index": 4}


def is_favorite_element(element: str) -> bool:
    """判断是否为喜用神五行"""
    return element in PROFILE["favorite_elements"]


def is_unfavorable_element(element: str) -> bool:
    """判断是否为忌神五行"""
    return element in PROFILE["unfavorable_elements"]


def get_analysis_context() -> Dict:
    """获取分析上下文信息"""
    today = date.today()
    current_dayun = get_current_dayun(today)
    
    next_dayun = None
    if current_dayun["index"] + 1 < len(PROFILE["dayun"]):
        next_dayun = PROFILE["dayun"][current_dayun["index"] + 1]
    
    return {
        "today": today,
        "current_dayun": current_dayun,
        "next_dayun": next_dayun,
        "birth_chart": BIRTH_CHART,
        "profile": PROFILE,
    }
