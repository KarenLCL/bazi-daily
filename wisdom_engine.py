"""
八字之神·智慧引擎
从每日反馈中提炼命理规律，反哺未来的运势解读

流程：象(反馈) → 数(干支参数) → 理(智慧规律) → 应用到未来日子
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

from bazi_engine import (
    HEAVENLY_STEMS, EARTHLY_BRANCHES,
    get_day_stem_branch, get_bazi_pillar_name,
    get_branch_relation, get_ten_god,
    get_five_element_from_stem, get_five_element_from_branch,
    get_year_stem_branch, calculate_daily_score,
)
from user_profile import BIRTH_CHART, PROFILE, get_current_dayun
from dayun_weights import get_dayun_weight
from database import get_recent_feedback, get_feedback_by_date


class WisdomEngine:
    """智慧引擎 - 从反馈中学习命理规律"""
    
    def __init__(self):
        self.birth_day_stem = BIRTH_CHART["day"]["stem"]
        self.birth_day_branch = BIRTH_CHART["day"]["branch"]
        self.wisdom_db = {}  # cache
    
    def refresh_wisdom(self) -> Dict:
        """重新从所有反馈中提炼智慧"""
        feedbacks = get_recent_feedback(365)  # 近一年
        if not feedbacks:
            return {"patterns": [], "total_days": 0}
        
        # 按不同维度分组
        groups = {
            "branch_relation": defaultdict(list),  # 地支关系维度
            "ten_god": defaultdict(list),          # 十神维度
            "day_element": defaultdict(list),      # 日干五行维度
            "branch_element": defaultdict(list),   # 日支五行维度
            "season": defaultdict(list),           # 季节维度
            "dayun": defaultdict(list),            # 大运维度
        }
        
        for fb in feedbacks:
            try:
                d = date.fromisoformat(fb['date'])
                ds, db = get_day_stem_branch(d)
                pillar = get_bazi_pillar_name(ds, db)
                ten_god = get_ten_god(self.birth_day_stem, ds)
                stem_elem = get_five_element_from_stem(ds)
                branch_elem = get_five_element_from_branch(db)
                relations = get_branch_relation(db, self.birth_day_branch)
                month = d.month
                
                # 季节
                if 3 <= month <= 5: season = "春季木旺"
                elif 6 <= month <= 8: season = "夏季火旺"
                elif 9 <= month <= 11: season = "秋季金旺"
                else: season = "冬季水旺"
                
                # 大运
                dayun = get_current_dayun(d)
                
                score = fb.get('prediction_score', 0) or 0
                accuracy = fb.get('accuracy_rating', 0) or 0
                actual = fb.get('actual_rating', 0) or 0
                
                entry = {
                    "date": d,
                    "pillar": pillar,
                    "stem": ds, "branch": db,
                    "ten_god": ten_god,
                    "stem_elem": stem_elem, "branch_elem": branch_elem,
                    "relations": relations,
                    "season": season,
                    "dayun": dayun['name'],
                    "score": score,
                    "accuracy": accuracy,
                    "actual": actual,
                    "feedback": (fb.get('actual_feedback', '') or '')[:80],
                }
                
                # 按地支关系分组
                for rel in relations or ['平']:
                    groups["branch_relation"][rel].append(entry)
                
                # 按十神分组
                groups["ten_god"][ten_god].append(entry)
                
                # 按五行分组
                groups["day_element"][stem_elem].append(entry)
                groups["branch_element"][branch_elem].append(entry)
                
                # 按季节
                groups["season"][season].append(entry)
                
                # 按大运
                groups["dayun"][dayun['name']].append(entry)
                
            except Exception:
                continue
        
        # 提炼智慧
        patterns = []
        for dim_name, dim_groups in groups.items():
            for key, entries in dim_groups.items():
                if len(entries) < 2:
                    continue  # 数据太少，不足以形成规律
                
                avg_acc = sum(e['accuracy'] for e in entries) / len(entries)
                avg_act = sum(e['actual'] for e in entries) / len(entries)
                avg_score = sum(e['score'] for e in entries) / len(entries)
                
                pattern = {
                    "dimension": dim_name,
                    "key": key,
                    "count": len(entries),
                    "avg_score": round(avg_score, 1),
                    "avg_accuracy": round(avg_acc, 1),
                    "avg_actual": round(avg_act, 1),
                    "entries": sorted(entries, key=lambda x: x['date']),
                }
                
                # 根据数据生成智慧语句
                pattern["wisdom"] = self._generate_wisdom(pattern)
                patterns.append(pattern)
        
        # 排序：数据量越多、规律越明显的排前面
        patterns.sort(key=lambda p: (p['count'], abs(p['avg_accuracy'] - 3)), reverse=True)
        
        self.wisdom_db = {
            "patterns": patterns,
            "total_days": len(feedbacks),
            "generated_at": datetime.now().isoformat(),
        }
        return self.wisdom_db
    
    def _generate_wisdom(self, pattern: Dict) -> str:
        """根据数据生成智慧语句"""
        dim = pattern['dimension']
        key = pattern['key']
        count = pattern['count']
        avg_acc = pattern['avg_accuracy']
        avg_act = pattern['avg_actual']
        avg_score = pattern['avg_score']
        
        # 根据准确度判断规律强弱
        confidence = ""
        if avg_acc >= 4.0 and count >= 3:
            confidence = "✅ 已验证规律"
        elif avg_acc >= 3.5 and count >= 2:
            confidence = "📊 初步发现"
        else:
            confidence = "🔍 有待观察"
        
        # 各维度的智慧模板
        if dim == "branch_relation":
            templates = {
                "合": "合化日能量易被合走，容易感到消耗。建议重要事项安排在上午，下午留时间给自己充电。",
                "冲": "相冲日能量波动较大，容易有突发状况或情绪起伏。宜静不宜动，避免重大决定。",
                "刑": "相刑日易有小人是非或人际摩擦。言辞需谨慎，能不说的先不说。",
                "害": "相害日要注意人际关系的微妙变化，特别是合作和沟通方面。",
                "平": "无特殊冲刑合害的日子，能量相对平稳。",
            }
            wisdom = templates.get(key, f"{key}日需留意当天的地支关系对你的影响。")
            
        elif dim == "ten_god":
            templates = {
                "正官": "正官日适合按规则办事，与上级沟通会比较顺利。",
                "七杀": "七杀日压力偏大，遇到挑战要保持冷静，以柔克刚。",
                "正印": "正印日适合学习、思考和接受帮助。",
                "偏印": "偏印日灵感丰富，适合独立研究或创作。",
                "比肩": "比肩日有同行或朋友相助，团队协作效率高。",
                "劫财": "劫财日人际活跃但注意支出，适合合作但不宜投资。",
                "食神": "食神日心情愉悦、表达顺畅，适合展示才华和社交。",
                "伤官": "伤官日想法多但言辞易伤人，注意控制表达方式。",
                "正财": "正财日财运稳定，适合处理财务规划和结算。",
                "偏财": "偏财日有机会也有风险，不宜投机。",
            }
            wisdom = templates.get(key, f"{key}日在{key}方面需特别留意。")
            
        elif dim == "season":
            templates = {
                "春季木旺": "春季木旺，你需要多用土金来平衡。穿米色/白色，少吃生发食物。",
                "夏季火旺": "夏季火旺，注意降心火，多喝水，避免在烈日下久待。",
                "秋季金旺": "秋季金旺，是你的好季节！能量充沛，适合推进重要事项。",
                "冬季水旺": "冬季水旺，注意保暖防寒，水泄金气不宜过度劳累。",
            }
            wisdom = templates.get(key, f"{key}需注意季节变化对你命局的影响。")
            
        elif dim == "day_element":
            if key in PROFILE.get("favorite_elements", []):
                wisdom = f"{key}日是你的喜用神日，整体能量向好，适合主动推进事情。"
            elif key in PROFILE.get("unfavorable_elements", []):
                wisdom = f"{key}日是你的忌神日，建议以守为主，减少不必要的变动和消耗。"
            else:
                wisdom = f"{key}日能量中性，按部就班即可。"
                
        elif dim == "dayun":
            weight = get_dayun_weight(key)
            if weight >= 10:
                wisdom = f"{key}大运整体对你非常有利，这步运中你的能量状态比以往好很多。把握机会！"
            elif weight > 0:
                wisdom = f"{key}大运对你有一定的帮助，整体趋势向好。"
            else:
                wisdom = f"{key}大运中需要更加注重自我保护和能量管理。"
        
        else:
            wisdom = f"根据{count}天的数据观察，{key}日你的平均评分{avg_score}分。"
        
        return f"{confidence}：{wisdom}"
    
    def get_wisdom_for_today(self, target_date: date = None) -> Dict:
        """获取今天匹配的智慧提醒"""
        if target_date is None:
            target_date = date.today()
        
        if not self.wisdom_db or 'patterns' not in self.wisdom_db:
            self.refresh_wisdom()
        
        ds, db = get_day_stem_branch(target_date)
        ten_god = get_ten_god(self.birth_day_stem, ds)
        stem_elem = get_five_element_from_stem(ds)
        branch_elem = get_five_element_from_branch(db)
        relations = get_branch_relation(db, self.birth_day_branch)
        
        month = target_date.month
        if 3 <= month <= 5: season = "春季木旺"
        elif 6 <= month <= 8: season = "夏季火旺"
        elif 9 <= month <= 11: season = "秋季金旺"
        else: season = "冬季水旺"
        
        dayun = get_current_dayun(target_date)
        
        today_wisdom = []
        
        for pattern in self.wisdom_db.get('patterns', []):
            dim = pattern['dimension']
            key = pattern['key']
            match = False
            
            if dim == "branch_relation":
                match = key in relations or (not relations and key == "平")
            elif dim == "ten_god":
                match = key == ten_god
            elif dim == "day_element":
                match = key == stem_elem
            elif dim == "branch_element":
                match = key == branch_elem
            elif dim == "season":
                match = key == season
            elif dim == "dayun":
                match = key == dayun['name']
            
            if match and pattern['count'] >= 2:
                today_wisdom.append({
                    "wisdom": pattern['wisdom'],
                    "confidence": pattern['count'],
                    "avg_score": pattern['avg_score'],
                    "data_points": pattern['count'],
                })
        
        # 有限排序：数据点多的优先
        today_wisdom.sort(key=lambda w: w['data_points'], reverse=True)
        
        return {
            "date": target_date,
            "matches": today_wisdom[:3],  # 最多3条
            "total_patterns": len(self.wisdom_db.get('patterns', [])),
            "total_feedback_days": self.wisdom_db.get('total_days', 0),
        }
    
    def get_wisdom_summary(self) -> Dict:
        """获取智慧总结（用于报告页）"""
        if not self.wisdom_db:
            self.refresh_wisdom()
        
        # 按维度汇总
        by_dim = defaultdict(list)
        for p in self.wisdom_db.get('patterns', []):
            by_dim[p['dimension']].append(p)
        
        # 找出最可靠的规律（数据最多且准确率高）
        top_patterns = sorted(
            [p for p in self.wisdom_db.get('patterns', []) if p['count'] >= 2],
            key=lambda p: (p['count'], p['avg_accuracy']),
            reverse=True
        )[:5]
        
        return {
            "total_days": self.wisdom_db.get('total_days', 0),
            "total_patterns": len(self.wisdom_db.get('patterns', [])),
            "top_patterns": top_patterns,
            "by_dimension": dict(by_dim),
        }


# 全局引擎实例
wisdom_engine = WisdomEngine()
