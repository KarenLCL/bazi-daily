"""
命理引擎核心模块
基于用户已验证的命盘数据进行干支计算
作者：专属命理工具 for Karen
"""

from datetime import date, datetime, timedelta
from typing import Tuple, List, Dict, Optional
import math

# ============ 基础常量 ============

# 十天干
HEAVENLY_STEMS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
# 十二地支
EARTHLY_BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 天干五行
STEM_ELEMENT = ['木', '木', '火', '火', '土', '土', '金', '金', '水', '水']
# 地支五行
BRANCH_ELEMENT = ['水', '土', '木', '木', '土', '火', '火', '土', '金', '金', '土', '水']

# 天干阴阳 (0=阳, 1=阴)
STEM_YIN_YANG = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
# 地支阴阳
BRANCH_YIN_YANG = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]

# 藏干 (地支 -> 藏干列表)
HIDDEN_STEMS = {
    0: [9],           # 子: 癸
    1: [5, 9, 7],     # 丑: 己癸辛
    2: [0, 2, 4],     # 寅: 甲丙戊
    3: [1],           # 卯: 乙
    4: [4, 1, 9],     # 辰: 戊乙癸
    5: [2, 6, 4],     # 巳: 丙庚戊
    6: [3, 5],        # 午: 丁己
    7: [5, 3, 1],     # 未: 己丁乙
    8: [6, 8, 4],     # 申: 庚壬戊
    9: [7],            # 酉: 辛
    10: [4, 7, 3],    # 戌: 戊辛丁
    11: [8, 0]         # 亥: 壬甲
}

# 地支六合
LIU_HE = {
    0: 1,   # 子丑合
    1: 0,   # 丑子合
    2: 11,  # 寅亥合
    3: 10,  # 卯戌合
    4: 9,   # 辰酉合
    5: 8,   # 巳申合
    6: 7,   # 午未合
    7: 6,   # 未午合
    8: 5,   # 申巳合
    9: 4,   # 酉辰合
    10: 3,  # 戌卯合
    11: 2   # 亥寅合
}

# 六冲
LIU_CHONG = {
    0: 6,   # 子午冲
    1: 7,   # 丑未冲
    2: 8,   # 寅申冲
    3: 9,   # 卯酉冲
    4: 10,  # 辰戌冲
    5: 11,  # 巳亥冲
    6: 0,   # 午子冲
    7: 1,   # 未丑冲
    8: 2,   # 申寅冲
    9: 3,   # 酉卯冲
    10: 4,  # 戌辰冲
    11: 5   # 亥巳冲
}

# 三刑
SAN_XING = {
    0: 3,   # 子卯刑 (无礼之刑)
    3: 0,   # 卯子刑
    1: 7,   # 丑未戌三刑 (无恩之刑)
    7: 1,
    10: 1,
    8: 8,   # 寅巳申三刑 (无恩之刑)
    5: 5,
    2: 2,
    6: 6,   # 午午自刑
    9: 9,   # 酉酉自刑
    11: 11  # 亥亥自刑
}

# 地支三合
SAN_HE = {
    # 申子辰合水
    8: (0, 4),
    0: (8, 4),
    4: (8, 0),
    # 亥卯未合木
    11: (3, 7),
    3: (11, 7),
    7: (11, 3),
    # 寅午戌合火
    2: (6, 10),
    6: (2, 10),
    10: (2, 6),
    # 巳酉丑合金
    5: (9, 1),
    9: (5, 1),
    1: (5, 9)
}

# 纳音纳䇽表 (60甲子纳音)
NAYIN_TABLE = [
    "海中金", "炉中火", "大林木", "路旁土", "剑锋金", "山头火",
    "涧下水", "城墙土", "白蜡金", "杨柳木", "泉中水", "屋上土",
    "霹雳火", "松柏木", "长流水", "砂石金", "山下火", "平地木",
    "壁上土", "金箔金", "覆灯火", "天河水", "大驿土", "钗钏金",
    "桑柘木", "大溪水", "沙中土", "天上火", "石榴木", "大海水"
]

# 天干相合
STEM_HE = {
    0: 5,   # 甲己合
    1: 4,   # 乙庚合
    2: 7,   # 丙辛合
    3: 6,   # 丁壬合
    4: 1,   # 戊癸合
    5: 0,
    6: 3,
    7: 2,
    8: 9,   # 任意？不，壬丁合
    9: 8    # 癸戊合
}

# 六十甲子 (60天干地支组合)
JIAZI_CYCLE = [(i % 10, i % 12) for i in range(60)]

# 时柱天干速查表 (根据日干)
# 日干索引 -> 子时天干索引
HOUR_STEM_TABLE = {
    0: 0,   # 甲日 -> 甲子
    1: 2,   # 乙日 -> 丙子
    2: 4,   # 丙日 -> 戊子
    3: 6,   # 丁日 -> 庚子
    4: 8,   # 戊日 -> 壬子
    5: 0,   # 己日 -> 甲子
    6: 2,   # 庚日 -> 丙子
    7: 4,   # 辛日 -> 戊子
    8: 6,   # 壬日 -> 庚子
    9: 8    # 癸日 -> 壬子
}

# 十二时辰对应地支
TWO_HOUR_PERIODS = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# ============ 参考日期：1900-01-01 = 甲戌日 ============
REFERENCE_DATE = date(1900, 1, 1)
REF_STEM = 0   # 甲
REF_BRANCH = 10  # 戌


def get_day_stem_branch(target_date: date) -> Tuple[int, int]:
    """计算指定日期的日干支 (天干索引, 地支索引)"""
    delta = (target_date - REFERENCE_DATE).days
    stem = (REF_STEM + delta) % 10
    branch = (REF_BRANCH + delta) % 12
    return stem, branch


def get_hour_stem_branch(day_stem: int, hour_branch: int) -> Tuple[int, int]:
    """计算指定时辰的时柱 (天干索引, 地支索引)
    day_stem: 日干索引
    hour_branch: 时辰地支索引 (辰时=4)
    """
    first_hour_stem = HOUR_STEM_TABLE[day_stem]
    hour_stem = (first_hour_stem + hour_branch) % 10
    return hour_stem, hour_branch


def get_year_stem_branch(year: int) -> Tuple[int, int]:
    """计算指定年份的年干支"""
    # 年柱以立春为界，简化版以农历年为准
    # 1984 = 甲子年
    offset = year - 1984
    if year >= 1984:
        stem = offset % 10
        branch = offset % 12
    else:
        stem = (offset % 10 + 10) % 10
        branch = (offset % 12 + 12) % 12
    return stem, branch


def get_month_stem_branch(year_stem: int, lunar_month: int) -> Tuple[int, int]:
    """计算指定月份 (农历月) 的月干支
    year_stem: 年干索引
    lunar_month: 农历月份 (1-12)
    """
    # 寅月为正月
    # 甲己之年丙作首，乙庚之岁戊为头
    # 丙辛必定寻庚起，丁壬壬位顺行流
    # 若问戊癸何方发，甲寅之上好追求
    first_month_stem_table = {
        0: 2,   # 甲年 -> 丙寅
        1: 4,   # 乙年 -> 戊寅
        2: 6,   # 丙年 -> 庚寅
        3: 8,   # 丁年 -> 壬寅
        4: 0,   # 戊年 -> 甲寅
        5: 2,   # 己年 -> 丙寅
        6: 4,   # 庚年 -> 戊寅
        7: 6,   # 辛年 -> 庚寅
        8: 8,   # 壬年 -> 壬寅
        9: 0    # 癸年 -> 甲寅
    }
    first_month_stem = first_month_stem_table[year_stem]
    # 正月地支为寅 (index 2), 二月卯 (3), 三月辰 (4), ...
    month_branch = (lunar_month + 1) % 12  # 正月=寅(2), 二月=卯(3), ...
    month_stem = (first_month_stem + lunar_month - 1) % 10
    return month_stem, month_branch


def get_nayin(stem: int, branch: int) -> str:
    """获取纳音五行"""
    index = (stem % 10) // 2  # 每两个天干一组
    # 60甲子纳音索引 = (stem//2 * 6 + branch//2) % 30... 过于简化
    # 使用更准确的方法
    jiazi_idx = -1
    for i, (s, b) in enumerate(JIAZI_CYCLE):
        if s == stem and b == branch:
            jiazi_idx = i
            break
    if jiazi_idx == -1:
        return "未知"
    # 每2个甲子对应一个纳音
    nayin_idx = jiazi_idx // 2
    return NAYIN_TABLE[nayin_idx] if nayin_idx < len(NAYIN_TABLE) else "未知"


def get_stem_relation(day_stem: int, target_stem: int) -> Dict:
    """计算天干关系 (相对于日主)
    返回: {relation, element, effect}
    """
    # 生克关系
    element_cycle = ['木', '木', '火', '火', '土', '土', '金', '金', '水', '水']
    day_elem = element_cycle[day_stem]
    target_elem = element_cycle[target_stem]
    
    # 五行生克: 木火土金水
    elem_order = ['木', '火', '土', '金', '水']
    day_elem_idx = elem_order.index(day_elem) if day_elem in elem_order else -1
    target_elem_idx = elem_order.index(target_elem) if target_elem in elem_order else -1
    
    if day_elem_idx == -1 or target_elem_idx == -1:
        return {"relation": "未知", "effect": 0}
    
    # 生我 (印)
    if (day_elem_idx - 1) % 5 == target_elem_idx:
        relation = "生我(印)"
        effect = 1  # 吉
    # 我生 (食伤)
    elif (day_elem_idx + 1) % 5 == target_elem_idx:
        relation = "我生(食伤)"
        effect = -1  # 泄身
    # 克我 (官杀)
    elif (day_elem_idx + 2) % 5 == target_elem_idx:
        relation = "克我(官杀)"
        effect = -1  # 克身
    # 我克 (财)
    elif (day_elem_idx - 2) % 5 == target_elem_idx:
        relation = "我克(财)"
        effect = -1  # 耗身
    else:
        relation = "同我(比劫)"
        effect = 1  # 帮身
    
    return {"relation": relation, "element": target_elem, "effect": effect}


def get_ten_god(day_stem: int, target_stem: int) -> str:
    """计算十神关系
    day_stem: 日主天干索引
    target_stem: 目标天干索引
    """
    same_yinyang = STEM_YIN_YANG[day_stem] == STEM_YIN_YANG[target_stem]
    
    element_cycle = ['木', '木', '火', '火', '土', '土', '金', '金', '水', '水']
    day_elem = element_cycle[day_stem]
    target_elem = element_cycle[target_stem]
    
    elem_order = ['木', '火', '土', '金', '水']
    day_elem_idx = elem_order.index(day_elem)
    target_elem_idx = elem_order.index(target_elem)
    
    # 生我者为印枭
    if (day_elem_idx - 1) % 5 == target_elem_idx:
        return "正印" if not same_yinyang else "偏印"
    # 我生者为食伤
    elif (day_elem_idx + 1) % 5 == target_elem_idx:
        return "食神" if same_yinyang else "伤官"
    # 克我者为官杀
    elif (day_elem_idx + 2) % 5 == target_elem_idx:
        return "正官" if not same_yinyang else "七杀"
    # 我克者为财
    elif (day_elem_idx - 2) % 5 == target_elem_idx:
        return "正财" if not same_yinyang else "偏财"
    # 同我者为比劫
    else:
        return "比肩" if same_yinyang else "劫财"


def get_branch_relation(branch1: int, branch2: int) -> List[str]:
    """计算地支关系: 冲刑合害"""
    relations = []
    
    # 六冲
    if LIU_CHONG.get(branch1) == branch2:
        relations.append("冲")
    
    # 六合
    if LIU_HE.get(branch1) == branch2:
        relations.append("合")
    
    # 三刑
    if branch1 == branch2:
        if branch1 in [6, 9, 11]:  # 午、酉、亥自刑
            relations.append("自刑")
    elif SAN_XING.get(branch1) == branch2 or SAN_XING.get(branch2) == branch1:
        relations.append("刑")
    
    # 三合 - 检查是否构成三合局中的两个
    if branch1 in SAN_HE:
        partners = SAN_HE[branch1]
        if branch2 in partners:
            relations.append("三合")
    
    # 六害 (地支相害)
    hai_pairs = [(0, 7), (1, 6), (2, 5), (3, 4), (8, 11), (9, 10)]  # 子未、午丑、寅巳、卯辰、申亥、酉戌
    for (a, b) in hai_pairs:
        if (branch1 == a and branch2 == b) or (branch1 == b and branch2 == a):
            relations.append("害")
            break
    
    return relations


def get_five_element_from_branch(branch: int) -> str:
    """获取地支的五行属性"""
    return BRANCH_ELEMENT[branch]


def get_five_element_from_stem(stem: int) -> str:
    """获取天干的五行属性"""
    return STEM_ELEMENT[stem]


def calculate_daily_score(day_stem: int, day_branch: int, 
                          birth_stem: int, birth_branch: int,
                          user_profile: Dict,
                          dayun_weight: int = 0) -> Dict:
    """计算每日运势评分和详细解读
    与用户的出生日柱进行比较分析
    dayun_weight: 大运加权值 (乙酉运+15, 丙戌运+5, 丁亥运-10等)
    """
    result = {
        "score": 50,  # 0-100
        "elements": {},
        "ten_gods": {},
        "relations": [],
        "details": []
    }
    
    # ---- 1. 日干关系分析 ----
    day_element = get_five_element_from_stem(day_stem)
    birth_element = get_five_element_from_stem(birth_stem)
    
    result["elements"]["日干"] = {
        "today": f"{HEAVENLY_STEMS[day_stem]}{day_element}",
        "birth": f"{HEAVENLY_STEMS[birth_stem]}{birth_element}",
        "relation": get_stem_relation(birth_stem, day_stem)
    }
    
    # ---- 2. 十神分析 ----
    ten_god = get_ten_god(birth_stem, day_stem)
    result["ten_gods"]["日干"] = {
        "stem": HEAVENLY_STEMS[day_stem],
        "ten_god": ten_god
    }
    
    # ---- 3. 地支关系 ----
    relations = get_branch_relation(day_branch, birth_branch)
    result["relations"] = relations
    
    result["details"].append({
        "type": "日柱",
        "content": f"今日日柱: {HEAVENLY_STEMS[day_stem]}{EARTHLY_BRANCHES[day_branch]} ({get_five_element_from_stem(day_stem)}{get_five_element_from_branch(day_branch)})"
    })
    
    # ---- 4. 评分计算 ----
    score = 50
    
    # 用神加分: 土(4,5索引) 金(6,7索引)
    favorite_stems = [4, 5, 6, 7]  # 戊己庚辛 (土金)
    favorite_branches = [1, 4, 7, 8, 9, 10]  # 丑辰未申酉戌 (土金)
    # 注: 巳中藏庚金, 但巳本身为火
    
    # 修正: 地支土=丑(1),辰(4),未(7),戌(10); 地支金=申(8),酉(9)
    favorite_branches_earth = [1, 4, 7, 10]  # 土支
    favorite_branches_metal = [8, 9]  # 金支
    
    # 忌神: 木(0,1索引) 火(2,3索引)
    unfavorable_stems = [0, 1, 2, 3]  # 甲乙丙丁 (木火)
    unfavorable_branches_wood = [2, 3, 11]  # 寅卯亥(亥中藏甲木)
    unfavorable_branches_fire = [5, 6]  # 巳午
    
    # 天干评分
    if day_stem in favorite_stems:
        score += 15
        result["details"].append({
            "type": "加分",
            "content": f"✓ 今日天干{HEAVENLY_STEMS[day_stem]}({get_five_element_from_stem(day_stem)})为喜用神，对你有利"
        })
    elif day_stem in unfavorable_stems:
        score -= 15
        result["details"].append({
            "type": "减分",
            "content": f"✗ 今日天干{HEAVENLY_STEMS[day_stem]}({get_five_element_from_stem(day_stem)})为忌神，需多加注意"
        })
    
    # 地支评分
    if day_branch in favorite_branches_earth or day_branch in favorite_branches_metal:
        score += 10
        elem = get_five_element_from_branch(day_branch)
        result["details"].append({
            "type": "加分",
            "content": f"✓ 今日地支{EARTHLY_BRANCHES[day_branch]}({elem})为喜用神"
        })
    elif day_branch in unfavorable_branches_wood or day_branch in unfavorable_branches_fire:
        score -= 10
        elem = get_five_element_from_branch(day_branch)
        result["details"].append({
            "type": "减分",
            "content": f"✗ 今日地支{EARTHLY_BRANCHES[day_branch]}({elem})为忌神"
        })
    
    # 冲刑关系减分
    if "冲" in relations:
        score -= 15
        result["details"].append({
            "type": "警告",
            "content": f"⚠ 今日地支与您的日支相冲，能量波动较大，宜静不宜动"
        })
    if "刑" in relations:
        score -= 10
        result["details"].append({
            "type": "注意",
            "content": f"△ 今日地支与您日支相刑，易有小人是非，言行需谨慎"
        })
    if "害" in relations:
        score -= 5
        result["details"].append({
            "type": "提示",
            "content": f"△ 今日地支与您日支相害，注意人际关系的微妙变化"
        })
    if "合" in relations:
        score += 8
        result["details"].append({
            "type": "加分",
            "content": f"✓ 今日地支与您日支相合，人缘佳，事情易成"
        })
    
    # 纳音加分
    # 金命纳音加分
    nayin = get_nayin(day_stem, day_branch)
    metal_nayin = ["海中金", "剑锋金", "白蜡金", "金箔金", "钗钏金", "沙中金"]
    earth_nayin = ["路旁土", "城墙土", "屋上土", "壁上土", "大驿土", "沙中土"]
    if nayin in metal_nayin:
        score += 5
        result["details"].append({
            "type": "加分",
            "content": '✓ 今日纳音「' + nayin + '」属金，与您命局相生'
        })
    elif nayin in earth_nayin:
        score += 3
        result["details"].append({
            "type": "加分",
            "content": '✓ 今日纳音「' + nayin + '」属土，与您命局相生'
        })
    
    # 限制评分范围
    score = max(0, min(100, score))
    
    # 大运加权
    score += dayun_weight
    score = max(0, min(100, score))
    result["score"] = score
    
    # 等级 (配色使用喜用神土金色系)
    if result["score"] >= 80:
        result["level"] = "大吉"
        result["color"] = "#fff8e1"
    elif result["score"] >= 65:
        result["level"] = "吉"
        result["color"] = "#f5f0eb"
    elif result["score"] >= 45:
        result["level"] = "平"
        result["color"] = "#efebe9"
    elif result["score"] >= 30:
        result["level"] = "不佳"
        result["color"] = "#e0e0e0"
    else:
        result["level"] = "谨慎"
        result["color"] = "#d7ccc8"
    
    return result


def get_bazi_pillar_name(stem: int, branch: int) -> str:
    """获取干支组合名称"""
    return f"{HEAVENLY_STEMS[stem]}{EARTHLY_BRANCHES[branch]}"


def get_hour_branch_from_time(hour: int, minute: int) -> int:
    """根据小时分钟获取时辰地支索引"""
    # 23:00-00:59 = 子(0), 01:00-02:59 = 丑(1), ...
    # 07:00-08:59 = 辰(4)
    time_decimal = hour + minute / 60.0
    if time_decimal >= 23 or time_decimal < 1:
        return 0  # 子
    elif 1 <= time_decimal < 3:
        return 1  # 丑
    elif 3 <= time_decimal < 5:
        return 2  # 寅
    elif 5 <= time_decimal < 7:
        return 3  # 卯
    elif 7 <= time_decimal < 9:
        return 4  # 辰
    elif 9 <= time_decimal < 11:
        return 5  # 巳
    elif 11 <= time_decimal < 13:
        return 6  # 午
    elif 13 <= time_decimal < 15:
        return 7  # 未
    elif 15 <= time_decimal < 17:
        return 8  # 申
    elif 17 <= time_decimal < 19:
        return 9  # 酉
    elif 19 <= time_decimal < 21:
        return 10  # 戌
    else:
        return 11  # 亥


def calculate_daily_bazi(target_date: date, hour: int = 8, minute: int = 0) -> Dict:
    """计算指定日期、指定时辰的八字四柱"""
    # 年柱
    year_stem, year_branch = get_year_stem_branch(target_date.year)
    
    # 月柱 (简化: 基于月份)
    # 立春(2月4日左右)为寅月
    month = target_date.month
    day_of_month = target_date.day
    
    # 大致判断节气月 (简化版)
    solar_month = month - 1  # 1月约等于丑月
    if day_of_month >= 4 and month == 2:
        solar_month = 1  # 2月4日后为寅月
    elif month == 1 and day_of_month >= 6:
        solar_month = 0  # 1月6日后约为丑月
    elif month == 12 and day_of_month >= 7:
        solar_month = 11  # 大雪后为子月
    
    # 简化: 公历月份转农历月 (近似)
    lunar_month_map = {1: 12, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: 8, 10: 9, 11: 10, 12: 11}
    approx_lunar_month = lunar_month_map.get(month, 1)
    
    month_stem, month_branch = get_month_stem_branch(year_stem, approx_lunar_month)
    
    # 日柱
    day_stem, day_branch = get_day_stem_branch(target_date)
    
    # 时柱 (指定时辰)
    hour_branch = get_hour_branch_from_time(hour, minute)
    hour_stem, hour_branch_calc = get_hour_stem_branch(day_stem, hour_branch)
    
    # 纳音
    day_nayin = get_nayin(day_stem, day_branch)
    
    return {
        "date": target_date,
        "year": {"stem": year_stem, "branch": year_branch, "name": get_bazi_pillar_name(year_stem, year_branch)},
        "month": {"stem": month_stem, "branch": month_branch, "name": get_bazi_pillar_name(month_stem, month_branch)},
        "day": {"stem": day_stem, "branch": day_branch, "name": get_bazi_pillar_name(day_stem, day_branch), "nayin": day_nayin},
        "hour": {"stem": hour_stem, "branch": hour_branch, "name": get_bazi_pillar_name(hour_stem, hour_branch)},
        "time_period": f"{hour:02d}:{minute:02d}"
    }


def get_month_boundaries(year: int) -> List[date]:
    """获取一年中各节气的大致日期 (简化版，用于月柱的精确计算)"""
    # 这是简化版本，精确节气需要天文计算
    # 这里返回每个月1号作为近似
    boundaries = []
    for m in range(1, 13):
        boundaries.append(date(year, m, 1))
    return boundaries


def get_day_five_element_detail(day_stem: int, day_branch: int, user_profile: Dict) -> List[str]:
    """生成日干支五行的详细解读"""
    details = []
    
    stem_elem = get_five_element_from_stem(day_stem)
    branch_elem = get_five_element_from_branch(day_branch)
    
    fav_elements = user_profile.get("favorite_elements", ["土", "金"])
    unfav_elements = user_profile.get("unfavorable_elements", ["木", "火"])
    
    details.append(f"日干【{HEAVENLY_STEMS[day_stem]}】属{stem_elem}，地支【{EARTHLY_BRANCHES[day_branch]}】属{branch_elem}")
    
    if stem_elem in fav_elements:
        details.append(f"天干{stem_elem}为喜用神，今日思维清晰，做事顺遂")
    elif stem_elem in unfav_elements:
        details.append(f"天干{stem_elem}为忌神，今日容易冲动或疲惫，需多加留意")
    
    if branch_elem in fav_elements:
        details.append(f"地支{branch_elem}也为喜，根基较稳，大事可谋")
    elif branch_elem in unfav_elements:
        details.append(f"地支{branch_elem}为忌，注意外在环境变化带来的压力")
    
    return details


def compare_with_birth_chart(daily_bazi: Dict, birth_chart: Dict) -> Dict:
    """将当日八字与出生八字进行全面比较分析"""
    comparison = {
        "day_vs_birth_day": {},
        "day_vs_birth_month": {},
        "day_vs_birth_year": {},
        "day_vs_birth_hour": {},
        "summary": []
    }
    
    day_stem = daily_bazi["day"]["stem"]
    day_branch = daily_bazi["day"]["branch"]
    
    birth_day_stem = birth_chart["day"]["stem"]
    birth_day_branch = birth_chart["day"]["branch"]
    
    # 与日柱比较
    day_relations = get_branch_relation(day_branch, birth_day_branch)
    day_ten_god = get_ten_god(birth_day_stem, day_stem)
    
    comparison["day_vs_birth_day"] = {
        "birth_pillar": birth_chart["day"]["name"],
        "today_pillar": daily_bazi["day"]["name"],
        "stem_ten_god": day_ten_god,
        "branch_relations": day_relations,
        "stem_relation": get_stem_relation(birth_day_stem, day_stem)
    }
    
    # 与大运比较
    if "current_dayun" in birth_chart:
        dayun = birth_chart["current_dayun"]
        dayun_stem = dayun["stem"]
        dayun_branch = dayun["branch"]
        
        stem_rel = get_stem_relation(birth_day_stem, dayun_stem)
        branch_rels = get_branch_relation(day_branch, dayun_branch)
        
        comparison["day_vs_dayun"] = {
            "dayun": dayun["name"],
            "stem_relation": stem_rel,
            "branch_relations": branch_rels
        }
    
    # 综合判断
    warnings = []
    positives = []
    
    # 判断当日与大运的关系
    if "day_vs_dayun" in comparison:
        dv = comparison["day_vs_dayun"]
        if "冲" in dv.get("branch_relations", []):
            warnings.append("今日与大运相冲，重要决策需谨慎")
        if "合" in dv.get("branch_relations", []):
            positives.append("今日与大运相合，事情容易推进")
    
    # 判断与日柱的关系
    dv2 = comparison["day_vs_birth_day"]
    if "冲" in dv2.get("branch_relations", []):
        warnings.append("今日地支与您日支相冲，情绪波动较大")
    if "合" in dv2.get("branch_relations", []):
        positives.append("今日地支与您日支相合，人缘运佳")
    
    comparison["summary"] = {
        "warnings": warnings,
        "positives": positives
    }
    
    return comparison
