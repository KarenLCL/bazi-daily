"""
力场引擎 - 量化八字中各种力量的生克合化刑害破冲
将n维的命理关系转化为可读的力场分析

原理: 八字是力与力之间的博弈
- 大运力量 > 流年力量 > 流月力量 > 流日力量 > 流时力量
- 十二长生决定每个干/支的能量状态（强弱）
- 生克合化刑害破冲是力的交互方式
"""

from datetime import date
from typing import Dict, List, Optional, Tuple

from bazi_engine import (
    HEAVENLY_STEMS, EARTHLY_BRANCHES, STEM_ELEMENT, BRANCH_ELEMENT,
    get_day_stem_branch, get_year_stem_branch, get_month_stem_branch,
    get_bazi_pillar_name, get_ten_god, get_branch_relation,
    get_five_element_from_stem, get_five_element_from_branch,
    get_hour_branch_from_time,
)
from user_profile import BIRTH_CHART, PROFILE, get_current_dayun
from dayun_weights import get_dayun_weight


# ============================================================
#  十二长生表 (天干索引 -> 地支索引 -> 阶段)
#  0=长生,1=沐浴,2=冠带,3=临官,4=帝旺,5=衰,6=病,7=死,8=墓,9=绝,10=胎,11=养
# ============================================================

LIFE_STAGES = {
    # 甲木
    0: {11:0, 0:1, 1:2, 2:3, 3:4, 4:5, 5:6, 6:7, 7:8, 8:9, 9:10, 10:11},
    # 乙木
    1: {6:0, 5:1, 4:2, 3:3, 2:4, 1:5, 0:6, 11:7, 10:8, 9:9, 8:10, 7:11},
    # 丙火
    2: {2:0, 3:1, 4:2, 5:3, 6:4, 7:5, 8:6, 9:7, 10:8, 11:9, 0:10, 1:11},
    # 丁火
    3: {9:0, 8:1, 7:2, 6:3, 5:4, 4:5, 3:6, 2:7, 1:8, 0:9, 11:10, 10:11},
    # 戊土 (同丙火)
    4: {2:0, 3:1, 4:2, 5:3, 6:4, 7:5, 8:6, 9:7, 10:8, 11:9, 0:10, 1:11},
    # 己土 (同丁火)
    5: {9:0, 8:1, 7:2, 6:3, 5:4, 4:5, 3:6, 2:7, 1:8, 0:9, 11:10, 10:11},
    # 庚金
    6: {5:0, 6:1, 7:2, 8:3, 9:4, 10:5, 11:6, 0:7, 1:8, 2:9, 3:10, 4:11},
    # 辛金
    7: {0:0, 11:1, 10:2, 9:3, 8:4, 7:5, 6:6, 5:7, 4:8, 3:9, 2:10, 1:11},
    # 壬水
    8: {8:0, 9:1, 10:2, 11:3, 0:4, 1:5, 2:6, 3:7, 4:8, 5:9, 6:10, 7:11},
    # 癸水
    9: {3:0, 2:1, 1:2, 0:3, 11:4, 10:5, 9:6, 8:7, 7:8, 6:9, 5:10, 4:11},
}

LIFE_STAGE_NAMES = ["长生","沐浴","冠带","临官","帝旺","衰","病","死","墓","绝","胎","养"]
LIFE_STAGE_POWER = {0:1.0, 1:0.8, 2:0.7, 3:0.8, 4:1.0, 5:0.6, 6:0.4, 7:0.2, 8:0.3, 9:0.1, 10:0.5, 11:0.5}
# 长生=最强, 帝旺=次强, 死/绝=最弱, 墓=收藏


def get_life_stage(stem: int, branch: int) -> Tuple[int, str, float]:
    """获取某天干在地支上的十二长生状态
    返回: (阶段索引, 阶段名称, 力量系数 0-1)
    """
    if stem in LIFE_STAGES and branch in LIFE_STAGES[stem]:
        stage = LIFE_STAGES[stem][branch]
        name = LIFE_STAGE_NAMES[stage]
        power = LIFE_STAGE_POWER[stage]
        return stage, name, power
    return -1, "未知", 0.0


class ForceEngine:
    """力场分析引擎"""
    
    def __init__(self):
        self.birth = BIRTH_CHART
        self.profile = PROFILE
    
    def analyze_daily_forces(self, target_date: date = None) -> Dict:
        """分析某一天的综合力场"""
        if target_date is None:
            target_date = date.today()
        
        ds, db = get_day_stem_branch(target_date)
        ys, yb = get_year_stem_branch(target_date.year)
        
        # 月柱 (简化)
        month = target_date.month
        approx_lm = month - 1 if month > 1 else 12
        ms, mb = get_month_stem_branch(ys, approx_lm - 1)
        
        # 辰时
        hs, hb = 4, 4  # 辰时
        
        current_dayun = get_current_dayun(target_date)
        du_stem = current_dayun['stem']
        du_branch = current_dayun['branch']
        
        # ===== 1. 十二长生分析 =====
        
        # 日主辛金在各柱的状态
        birth_day_stem = self.birth['day']['stem']  # 辛 = 7
        
        master_states = {
            "日主在年支": get_life_stage(birth_day_stem, self.birth['year']['branch']),
            "日主在月支": get_life_stage(birth_day_stem, self.birth['month']['branch']),
            "日主在日支": get_life_stage(birth_day_stem, self.birth['day']['branch']),
            "日主在时支": get_life_stage(birth_day_stem, self.birth['hour']['branch']),
            "日主在大运": get_life_stage(birth_day_stem, du_branch),
            "日主在流日": get_life_stage(birth_day_stem, db),
        }
        
        # ===== 2. 各层力量计算 =====
        
        # 基底: 日主自身的力量 = 长生状态 * 大运权重
        dayun_weight = get_dayun_weight(current_dayun['name'])
        
        # 日主力
        master_power = {
            "base": 50,  # 基准
            "dayun_boost": dayun_weight,
        }
        
        # 大运力量
        du_stem_fav = get_five_element_from_stem(du_stem) in self.profile['favorite_elements']
        du_branch_fav = get_five_element_from_branch(du_branch) in self.profile['favorite_elements']
        du_power = 0
        if du_stem_fav: du_power += 10
        if du_branch_fav: du_power += 10
        du_stage = get_life_stage(birth_day_stem, du_branch)
        du_power += int(du_stage[2] * 10)  # 长生状态加成
        
        # 流年力量
        y_stem_fav = get_five_element_from_stem(ys) in self.profile['favorite_elements']
        y_branch_fav = get_five_element_from_branch(yb) in self.profile['favorite_elements']
        y_power = 0
        if y_stem_fav: y_power += 8
        elif get_five_element_from_stem(ys) in self.profile['unfavorable_elements']: y_power -= 8
        if y_branch_fav: y_power += 8
        elif get_five_element_from_branch(yb) in self.profile['unfavorable_elements']: y_power -= 8
        _, _, y_stage_power = get_life_stage(birth_day_stem, yb)
        y_power += int(y_stage_power * 8)
        
        # 流月力量
        m_stem_fav = get_five_element_from_stem(ms) in self.profile['favorite_elements']
        m_branch_fav = get_five_element_from_branch(mb) in self.profile['favorite_elements']
        m_power = 0
        if m_stem_fav: m_power += 6
        elif get_five_element_from_stem(ms) in self.profile['unfavorable_elements']: m_power -= 6
        if m_branch_fav: m_power += 6
        elif get_five_element_from_branch(mb) in self.profile['unfavorable_elements']: m_power -= 6
        _, _, m_stage_power = get_life_stage(birth_day_stem, mb)
        m_power += int(m_stage_power * 6)
        
        # 流日力量
        d_stem_fav = get_five_element_from_stem(ds) in self.profile['favorite_elements']
        d_branch_fav = get_five_element_from_branch(db) in self.profile['favorite_elements']
        d_power = 0
        if d_stem_fav: d_power += 5
        elif get_five_element_from_stem(ds) in self.profile['unfavorable_elements']: d_power -= 5
        if d_branch_fav: d_power += 5
        elif get_five_element_from_branch(db) in self.profile['unfavorable_elements']: d_power -= 5
        _, _, d_stage_power = get_life_stage(birth_day_stem, db)
        d_power += int(d_stage_power * 5)
        
        # ===== 3. 地支交互力 =====
        interactions = []
        
        # 日支与各大支的关系
        pairs = [
            ("流日×日支", db, self.birth['day']['branch']),
            ("流日×大运", db, du_branch),
            ("流日×流年", db, yb),
            ("大运×流年", du_branch, yb),
        ]
        
        for label, b1, b2 in pairs:
            rels = get_branch_relation(b1, b2)
            for r in rels:
                force = 0
                if r == "冲": force = -15
                elif r == "刑": force = -8
                elif r == "害": force = -5
                elif r == "合": 
                    # 合看合的是什么五行
                    force = 5  # 合本身中性，具体要看合化结果
                elif r == "三合": force = 8
                interactions.append({
                    "pair": label,
                    "relation": r,
                    "force": force,
                    "desc": self._rel_description(r, b1, b2),
                })
        
        # ===== 4. 综合力场判断 =====
        total_force = master_power['base'] + master_power['dayun_boost'] + du_power + y_power + m_power + d_power
        for i in interactions:
            total_force += i['force']
        
        # 标准化到 0-100
        total_force = max(0, min(100, total_force))
        
        # ===== 5. 力量分级 =====
        levels = []
        forces = [
            ("大运", du_power, "largest"),
            ("流年", y_power, "large"),
            ("流月", m_power, "medium"),
            ("流日", d_power, "small"),
        ]
        
        # 找出主导力量
        max_force = max(abs(f[1]) for f in forces) if any(f[1] for f in forces) else 1
        for name, power, _ in forces:
            pct = int(abs(power) / max_force * 100) if max_force > 0 else 0
            levels.append({
                "name": name,
                "power": power,
                "percent": pct,
                "direction": "助" if power > 0 else "抑" if power < 0 else "平",
            })
        
        return {
            "date": target_date,
            "total_force": total_force,
            "master_states": master_states,
            "forces": forces,
            "levels": levels,
            "interactions": interactions,
            "dayun": current_dayun,
            "summary": self._generate_summary(total_force, levels, interactions),
        }
    
    def _rel_description(self, relation: str, b1: int, b2: int) -> str:
        """地支关系讲解"""
        descs = {
            "冲": f"地支{EARTHLY_BRANCHES[b1]}与{EARTHLY_BRANCHES[b2]}相冲，能量对冲剧烈",
            "合": f"地支{EARTHLY_BRANCHES[b1]}与{EARTHLY_BRANCHES[b2]}相合，能量汇聚",
            "刑": f"地支{EARTHLY_BRANCHES[b1]}与{EARTHLY_BRANCHES[b2]}相刑，能量纠结",
            "害": f"地支{EARTHLY_BRANCHES[b1]}与{EARTHLY_BRANCHES[b2]}相害，能量暗耗",
            "三合": f"地支{EARTHLY_BRANCHES[b1]}与{EARTHLY_BRANCHES[b2]}三合，能量共振",
            "自刑": f"地支{EARTHLY_BRANCHES[b1]}自刑，自我内耗",
        }
        return descs.get(relation, f"{relation}关系")
    
    def _generate_summary(self, total: int, levels: list, interactions: list) -> str:
        """生成综合判定"""
        if total >= 70:
            return "今日整体力场强劲，喜用神占主导，宜主动推进重要事项"
        elif total >= 55:
            return "今日力场偏正向，有利因素多于不利因素，按计划推进即可"
        elif total >= 40:
            return "今日力场中性，利弊相当，宜按部就班不宜冒进"
        elif total >= 25:
            return "今日力场偏弱，忌神力量较强，宜守不宜攻"
        else:
            return "今日力场低迷，多重压制，建议以静制动，减少消耗"
    
    def get_visual_forces(self, target_date: date = None) -> Dict:
        """获取可视化力场数据"""
        analysis = self.analyze_daily_forces(target_date)
        
        # 简化为可视化友好格式
        bars = []
        for f in analysis['levels']:
            bars.append({
                "label": f['name'],
                "value": f['power'],
                "percent": f['percent'],
                "direction": f['direction'],
                "bar_class": "bar-good" if f['power'] > 0 else "bar-bad" if f['power'] < 0 else "bar-neutral",
            })
        
        # 日主十二长生状态
        life_stages_vis = []
        for k, v in analysis['master_states'].items():
            life_stages_vis.append({
                "position": k,
                "stage": v[1],
                "power": v[2],
            })
        
        return {
            "total_score": analysis['total_force'],
            "bars": bars,
            "interactions": analysis['interactions'],
            "life_stages": life_stages_vis,
            "master_boost": analysis.get('dayun_boost', 0),
            "summary": analysis['summary'],
        }


force_engine = ForceEngine()
