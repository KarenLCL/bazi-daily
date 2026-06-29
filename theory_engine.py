"""
经典命理理论引擎
将八字经典理论编码为结构化知识，用于解读每日反馈中的象-数-理关系

理: 经典命理理论（十神本质、生克合化机理、十二长生含义）
数: 干支参数（当日八字+大运+流年）
象: 你实际发生的事（反馈内容）

流程: 象(你的生活) → 数(干支标记) → 理(经典解释) → 新的象(更好的建议)
"""

from datetime import date, datetime
from typing import Dict, List, Optional
from collections import defaultdict

from bazi_engine import (
    HEAVENLY_STEMS, EARTHLY_BRANCHES, STEM_ELEMENT, BRANCH_ELEMENT,
    get_day_stem_branch, get_bazi_pillar_name, get_ten_god,
    get_branch_relation, get_five_element_from_stem,
    get_five_element_from_branch, get_year_stem_branch,
    get_hour_branch_from_time,
)
from user_profile import BIRTH_CHART, PROFILE, get_current_dayun
from force_engine import get_life_stage, LIFE_STAGE_NAMES
from database import get_recent_feedback


# ============================================================
#  经典命理知识库
# ============================================================

TEN_GOD_THEORY = {
    "正官": {
        "essence": "正官者，克我而阴阳异。主规则、责任、上级、社会认可。",
        "when_favorable": "正官为用时，做事有章法，容易获得上级认可，适合按规矩办事。",
        "when_unfavorable": "正官为忌时，容易被规则束缚，感到压力，或遇到要求苛刻的上司。",
        "life_areas": ["事业", "名誉", "自律"],
        "keyword": "规则之力",
    },
    "七杀": {
        "essence": "七杀者，克我而阴阳同。主压力、挑战、权威、突破。",
        "when_favorable": "七杀为用时，能化压力为动力，遇到挑战反而激发潜力。",
        "when_unfavorable": "七杀为忌时，容易感到被逼迫、被压制，或被强势的人针对。",
        "life_areas": ["事业", "健康", "安全"],
        "keyword": "压力之力",
    },
    "正印": {
        "essence": "正印者，生我而阴阳异。主学习、长辈、庇护、学历。",
        "when_favorable": "正印为用时，学习效率高，容易得到长辈或贵人帮助。",
        "when_unfavorable": "正印为忌时，容易依赖他人，缺乏主见，或学习内容不实用。",
        "life_areas": ["学习", "家庭", "健康"],
        "keyword": "庇护之力",
    },
    "偏印": {
        "essence": "偏印者，生我而阴阳同。主偏门学问、灵感、独处、非物质追求。",
        "when_favorable": "偏印为用时，灵感丰富适合创意性工作，能读懂别人看不到的信息。",
        "when_unfavorable": "偏印为忌时，容易钻牛角尖，想太多，或沉迷虚无缥缈的事物。",
        "life_areas": ["思想", "灵感", "精神"],
        "keyword": "灵感之力",
    },
    "比肩": {
        "essence": "比肩者，同我而阴阳同。主自我、同辈、竞争、坚持。",
        "when_favorable": "比肩为用时，有主见，能和同辈相互支持，做事有毅力。",
        "when_unfavorable": "比肩为忌时，容易固执己见，或与同辈发生竞争冲突。",
        "life_areas": ["人际", "合作", "自我"],
        "keyword": "自我之力",
    },
    "劫财": {
        "essence": "劫财者，同我而阴阳异。主行动力、社交、破财、分享。",
        "when_favorable": "劫财为用时，行动力强，朋友多，适合团队协作。",
        "when_unfavorable": "劫财为忌时，容易被朋友拖累，或者因社交过度而消耗。",
        "life_areas": ["社交", "行动", "财务"],
        "keyword": "行动之力",
    },
    "食神": {
        "essence": "食神者，我生而阴阳同。主表达、享受、才华、福气。",
        "when_favorable": "食神为用时，心情好，表达流畅，有口福，适合展现才华。",
        "when_unfavorable": "食神为忌或被合化时，表达方式会变形——要么过于直接激烈（变伤官），要么有话说不出口。",
        "life_areas": ["表达", "创作", "享受"],
        "keyword": "表达之力",
    },
    "伤官": {
        "essence": "伤官者，我生而阴阳异。主才艺、言辞犀利、叛逆、不羁。",
        "when_favorable": "伤官为用时，聪明有才艺，适合艺术创作或技术工作。",
        "when_unfavorable": "伤官为忌时，言辞伤人，容易得罪人，或过度追求完美。",
        "life_areas": ["才华", "言辞", "自我"],
        "keyword": "锋芒之力",
    },
    "正财": {
        "essence": "正财者，我克而阴阳异。主稳定收入、妻子、资产、务实。",
        "when_favorable": "正财为用时，财运稳定，理财有方，适合做预算和规划。",
        "when_unfavorable": "正财为忌时，为财所累，或因财务问题感到焦虑。",
        "life_areas": ["财务", "婚姻", "物质"],
        "keyword": "稳定之力",
    },
    "偏财": {
        "essence": "偏财者，我克而阴阳同。主意外之财、投资、慷慨、社交。",
        "when_favorable": "偏财为用时，投资眼光好，社交中容易遇到贵人，出手大方。",
        "when_unfavorable": "偏财为忌时，容易破财，或被不靠谱的人和事吸引。",
        "life_areas": ["投资", "社交", "慷慨"],
        "keyword": "机遇之力",
    },
}

BRANCH_RELATION_THEORY = {
    "合": {
        "essence": "合者，阴阳相吸，两股力量汇聚。结果要么1+1>2（增益），要么能量被合走（消耗）。",
        "shen_combine": "巳申合化水。巳中藏丙庚戊，申中藏庚壬戊——你的日支巳与申相合后化为水（食伤）。",
        "you_combine": "酉为辛金之禄，辰为湿土印星。辰酉合金，增益日主。",
        "wu_combine": "午未合火，加重火势。你的日支巳遇午为巳午半会火局，同样加重忌神。",
    },
    "冲": {
        "essence": "冲者，相反力量正面碰撞。易有突发变化、搬迁、分离或重大转折。",
        "si_hai": "巳亥冲，水火相战。巳中丙火(正官)与亥中壬水(伤官)对冲，伤官见官，易与上级冲突或规则变动。",
        "mao_you": "卯酉冲，金木交战。酉为辛金之禄，卯为乙木偏财之根，冲则财禄相争，易为财务或价值观问题起冲突。",
    },
    "刑": {
        "essence": "刑者，能量纠结不顺。主摩擦、纠葛、或自我内耗。",
        "yin_si": "寅巳相刑，寅中甲木生巳中丙火，火旺克辛金。易因好心办坏事，或被别人的事牵连。",
    },
    "害": {
        "essence": "害者，暗中损耗。表面无事，实则能量被悄悄消耗。",
        "you_hai": "酉戌相害，戌为火库，燥土脆金。你前一日在酉(禄神)的高能量状态，次日转戌就被压制——昨天还精力充沛，今天就感觉提不起劲。",
        "shen_hai": "申亥相害，水旺泄金。申为辛金之帝旺，亥为辛金之死地，害则能量不续。",
    },
}

LIFE_STAGE_THEORY = {
    "长生": "如初生之婴，元气初生，宜养不宜用。",
    "沐浴": "如婴儿洗浴，生机勃勃但尚不稳定。",
    "冠带": "如少年加冠，渐成气候，可以开始做事。",
    "临官": "如官员上任，正式掌权，正当其时。",
    "帝旺": "如日中天，力量达到顶峰，但盛极将衰。",
    "衰": "如过午之日，力量开始衰退，宜收不宜放。",
    "病": "如人之染病，精气神不足，需休养。",
    "死": "如人之死亡，力量消亡，旧的不去新的不来。",
    "墓": "如入墓库，力量收藏沉淀，以待后用。",
    "绝": "如绝处逢生，力量断绝，但绝处有新机。",
    "胎": "如胚胎孕育，新力量正在酝酿中。",
    "养": "如胎养成形，蓄势待发，只欠东风。",
}

# 辛金日主专属理论
XIN_METAL_THEORY = {
    "essence": "辛金为珠玉之金，精致、敏感、有锋芒。喜壬水淘洗方显其华，喜土金为助。",
    "strength": "身弱之辛金，如未雕之玉，需外力打磨方能成器。",
    "spring": "生于寅月（初春），木气旺盛，财星当令。辛金在寅为胎地，力量微弱。",
    "preferred": "喜土金生扶，喜水淘洗。忌木火耗克。",
    "dayun_you": "乙酉大运，酉为辛金之临官（禄神）。身弱逢禄如久旱逢甘霖，届时能量状态会有质变。",
}


class TheoryEngine:
    """理论引擎 - 用经典八字理论解读每日反馈"""
    
    def __init__(self):
        self.birth = BIRTH_CHART
        self.profile = PROFILE
        self.annotations = []  # 积累的个人命理注疏
    
    def analyze_event(self, feedback_date: str, feedback_text: str,
                      day_stem: int, day_branch: int,
                      dimension: str = 'all') -> Dict:
        """分析一个反馈事件，连接理论"""
        ten_god = get_ten_god(self.birth['day']['stem'], day_stem)
        stem_elem = get_five_element_from_stem(day_stem)
        branch_elem = get_five_element_from_branch(day_branch)
        relations = get_branch_relation(day_branch, self.birth['day']['branch'])
        stage_idx, stage_name, stage_power = get_life_stage(self.birth['day']['stem'], day_branch)
        
        dayun = get_current_dayun(date.fromisoformat(feedback_date) if isinstance(feedback_date, str) else feedback_date)
        
        # 收集所有相关的理论
        theories = []
        
        # 十神理论
        if ten_god in TEN_GOD_THEORY and dimension in ('all', 'ten_god'):
            t = TEN_GOD_THEORY[ten_god]
            is_fav = get_five_element_from_stem(day_stem) in self.profile['favorite_elements']
            behavior = t['when_favorable'] if is_fav else t['when_unfavorable']
            theories.append({
                "type": "十神",
                "concept": f"{ten_god}日",
                "theory": t['essence'],
                "application": behavior,
                "keyword": t['keyword'],
            })
        
        # 地支关系理论
        if dimension in ('all', 'branch'):
            for rel in relations or ['平']:
                if rel in BRANCH_RELATION_THEORY:
                    bt = BRANCH_RELATION_THEORY[rel]
                    theories.append({
                        "type": "地支关系",
                        "concept": f"{rel}（{EARTHLY_BRANCHES[day_branch]}与日支{EARTHLY_BRANCHES[self.birth['day']['branch']]}）",
                        "theory": bt['essence'],
                        "application": bt.get(f'{EARTHLY_BRANCHES[day_branch]}_combine', ''),
                        "keyword": f"{rel}之力",
                    })
        
        # 十二长生理论
        if dimension in ('all', 'life_stage'):
            theories.append({
                "type": "十二长生",
                "concept": f"辛金在{EARTHLY_BRANCHES[day_branch]}为{stage_name}",
                "theory": LIFE_STAGE_THEORY.get(stage_name, ''),
                "application": f"力量系数: {stage_power:.1f}/1.0",
                "keyword": stage_name,
            })
        
        # 辛金特质
        theories.append({
            "type": "日主特质",
            "concept": "辛金日主",
            "theory": XIN_METAL_THEORY['essence'],
            "application": XIN_METAL_THEORY['strength'] if self.profile['day_master']['strength'] == '身弱' else '',
            "keyword": "珠玉之金",
        })
        
        # 大运
        du_weight = 0
        from dayun_weights import get_dayun_weight
        du_weight = get_dayun_weight(dayun['name'])
        if du_weight >= 10:
            theories.append({
                "type": "大运",
                "concept": f"{dayun['name']}大运",
                "theory": f"大运{dayun['name']}对日主{'大吉' if du_weight>=15 else '有利'}，能量加权{du_weight:+d}",
                "application": XIN_METAL_THEORY.get('dayun_you', ''),
                "keyword": f"{dayun['name']}运",
            })
        
        # 综合解读
        insight = self._synthesize(feedback_text, ten_god, relations, stage_name, theories, day_branch)
        
        return {
            "date": feedback_date,
            "pillar": get_bazi_pillar_name(day_stem, day_branch),
            "ten_god": ten_god,
            "relations": relations,
            "life_stage": (stage_name, stage_power),
            "theories": theories,
            "insight": insight,
        }
    
    def _synthesize(self, feedback: str, ten_god: str, relations: list, 
                    stage: str, theories: list, day_branch: int = -1) -> str:
        """从干支参数构建因果分析链——因为A干支关系→所以B能量状态→导致C生活体验"""
        parts = []
        birth_branch = self.birth['day']['branch']  # 巳=5
        
        # ========== 第一步：地支关系决定当日基调 ==========
        day_branch_name = EARTHLY_BRANCHES[day_branch] if 0 <= day_branch <= 11 else '?'
        birth_branch_name = EARTHLY_BRANCHES[birth_branch]
        
        # 提取各关系的优先解读——按合>冲>刑>害>平的优先级
        primary_rel = relations[0] if relations else '平'
        
        # 巳日主的地支关系表
        SI_RELATIONS = {
            # (地支序号): (关系, 解读)
            0: ('子', '合', '子与巳合——子水克巳火，合的本质是水灭火势。你的官星（丙火）受伤，今日在规则和权威面前容易感到无力。'),
            1: ('丑', '合', '丑与巳相合——丑为湿土，能生金晦火。对你而言，丑合巳等于有人帮你扑灭了多余的火气，印星护身，适合学习吸收。'),
            2: ('寅', '刑', '寅巳相刑——寅中甲木生巳中丙火，忌神木生忌神火，能量形成恶性循环。刑的实质是：木越多火越旺，火越旺你的压力越大。今日容易遇到让你纠结的小事。'),
            3: ('卯', '平', '卯为财星，与巳无特殊关系。财生官杀，今日的重点在资源与责任之间的平衡。'),
            4: ('辰', '合', '辰与巳相合——辰为湿土水库，合巳晦火生金。印库护身，能量被净化，适合整理和归纳。'),
            5: ('巳', '平', '两巳相见，能量重叠。火势翻倍，官杀力量大增。今日压力加倍，但熟稔的领域反而更从容。'),
            6: ('午', '会', '午巳半会火局——巳午火力叠加，官杀能量暴增。忌神火势燎原，今日外部压力大，宜静不宜动。'),
            7: ('未', '平', '未土生金，与巳无特殊刑冲。未为印库，印星得力，适合学习沉淀。'),
            8: ('申', '合', '巳申合化水——巳中丙火与申中庚金结合，转化为水。合的本质是能量转化：你的官星（火）和帮身（金）都被合走变成了水（食伤）。身弱逢合，等于你的力量被外界借走，所以容易感到被掏空。'),
            9: ('酉', '合', '巳酉半合金局——金的力量被放大。对身弱的你而言，这是友军到来，能量充值。酉又是你的禄神，今日状态会自然好转。'),
            10: ('戌', '害', '戌巳相害——戌为火库，燥土脆金。害是暗中消耗，你不会明显感到冲突，但发现事情推进起来比想象的累。'),
            11: ('亥', '冲', '巳亥相冲——水火交战，巳中丙火被亥中壬水正面冲击。这是力量最强的冲突模式，你的官星受损最严重。今日容易与上级、规则、权威正面碰撞。'),
        }
        
        if day_branch in SI_RELATIONS:
            r_name, r_type, r_desc = SI_RELATIONS[day_branch]
            if r_type == primary_rel or r_type in (relations or []):
                parts.append(r_desc)
            else:
                parts.append(f"今日地支为{day_branch_name}（{r_name}）。" + r_desc)
        else:
            # 十神兜底
            tg_map = {
                "正官": "正官为克我之阴阳异。官星主事，今日宜按规则办事，与上级沟通会比较顺畅。",
                "七杀": "七杀为克我之阴阳同。杀星当头，今日压力偏大，挑战多于机遇。",
                "正印": "正印为生我之阴阳异。印星护身，今日学习效率高，容易得到帮助。",
                "偏印": "偏印为生我之阴阳同。偏印主灵感，今日适合创造性工作。",
                "比肩": "比肩为同我之阴阳同。兄弟星现，今日适合团队协作。",
                "劫财": "劫财为同我之阴阳异。劫财主社交也主破耗，今日人际活跃但不宜涉及金钱往来。",
                "食神": "食神为我生之阴阳同。今日心情愉快，适合展现才华。",
                "伤官": "伤官为我生之阴阳异。今日表达欲强，你的话比平时更有杀伤力，要注意措辞。",
                "正财": "正财为我克之阴阳异。今日适合处理财务相关事务。",
                "偏财": "偏财为我克之阴阳同。今日社交机会增多但需保持清醒。",
            }
            parts.append(tg_map.get(ten_god, f"今日十神为{ten_god}。"))
        
        # ========== 第二步：十二长生修正能量感知 ==========
        stage_map = {
            "长生": "能量在上升期，但初生阶段不稳定，宜养不宜用。",
            "沐浴": "生机勃勃但不稳定，适合试验和探索。",
            "冠带": "渐成气候，适合开始新计划。",
            "临官": "身弱得禄为正，今日能量恰好够用，适合主动推进。",
            "帝旺": "力量达到顶峰但物极必反，身弱逢帝旺如回光返照——虽有力但不可持续，宜收不宜放。",
            "衰": "力量开始衰退，适合收尾和复盘。",
            "病": "精气神不足，不适合做重大决定。",
            "死": "能量低位运行，旧的不去新的不来。",
            "墓": "能量收藏沉淀，适合整理和内省。",
            "绝": "力量断绝，但绝处有新机，宜静待时机。",
            "胎": "新力量在酝酿中，宜规划不宜行动。",
            "养": "蓄势待发，宜准备不宜执行。",
        }
        if stage in stage_map:
            parts.append(f"能量层面：辛金在{day_branch_name}为{stage}——{stage_map[stage]}")
        
        # ========== 第三步：分析反馈中的因果印证 ==========
        if feedback and len(feedback) > 5:
            # 看看反馈是否符合干支预设的推论
            has_exhaustion = any(w in feedback for w in ['累','疼','困','疲惫','不想动'])
            has_conflict = any(w in feedback for w in ['怼','怒','气','吵','争','激烈'])
            has_creativity = any(w in feedback for w in ['做','写','设计','完成','做成了'])
            has_learning = any(w in feedback for w in ['学','听','读','看','了解','整理'])
            has_social = any(w in feedback for w in ['朋友','同事','一起','陪','聊','饭'])
            
            confirmations = []
            
            # 合日的消耗
            if primary_rel in ('合', '三合') and has_exhaustion:
                confirmations.append(f"地支逢合，能量被牵动——正是因为合的关系，你的精力才会被外界因素借走。这不是偶然，而是八字参数决定的气场流动。")
            
            # 冲日的冲突
            if primary_rel == '冲' and has_conflict:
                confirmations.append(f"地支逢冲，冲突的能量今日确实应验在了你的生活中——巳亥冲在现实中就是以人际关系冲突的方式体现的。")
            
            # 印星日的学习
            if ten_god in ('正印', '偏印') and has_learning:
                confirmations.append(f"印星日选择学习，这是八字能量在引导你——身弱喜印，今日的星象暗示了『输入优于输出』的行动策略。")
            
            # 食伤日的表达
            if ten_god in ('食神', '伤官') and (has_creativity or has_conflict):
                confirmations.append(f"食伤为表达星，今日你在表达和创造方面确实活跃。食伤泄身，你感到的消耗是正常的——身弱者逢食伤日，输出的能量都来自于本气的透支。")
            
            # 忌神日被动安静
            if ten_god in ('正官', '七杀') and has_learning and not has_conflict:
                confirmations.append(f"官杀日外部压力大，你选择把能量用在学习和内在积累上——这不是巧合，而是身弱之人在官杀日的本能反应：能量不够和外界的硬性要求对抗时，退而充电是最优解。")
            
            if confirmations:
                parts.append('——印证：' + ' '.join(confirmations))
        
        return '\n'.join(parts)
    
    def analyze_recent_feedback(self, days: int = 30) -> List[Dict]:
        """分析最近的反馈，积累注疏"""
        feedbacks = get_recent_feedback(days)
        results = []
        
        for fb in feedbacks:
            try:
                d = date.fromisoformat(fb['date'])
                ds, db = get_day_stem_branch(d)
                text = fb.get('actual_feedback', '') or ''
                if text:
                    analysis = self.analyze_event(fb['date'], text, ds, db)
                    results.append(analysis)
                    # 积累个人注疏
                    self.annotations.append({
                        "date": fb['date'],
                        "pillar": get_bazi_pillar_name(ds, db),
                        "ten_god": get_ten_god(self.birth['day']['stem'], ds),
                        "insight": analysis['insight'],
                        "feedback_excerpt": text[:60],
                    })
            except Exception:
                continue
        
        return results
    
    def get_today_theory(self, target_date: date = None) -> Dict:
        """获取今日的理论级解读"""
        if target_date is None:
            target_date = date.today()
        
        ds, db = get_day_stem_branch(target_date)
        ten_god = get_ten_god(self.birth['day']['stem'], ds)
        relations = get_branch_relation(db, self.birth['day']['branch'])
        stage_idx, stage_name, stage_power = get_life_stage(self.birth['day']['stem'], db)
        
        pillar = get_bazi_pillar_name(ds, db)
        
        # 查找往期同类日子的反馈
        similar_days = []
        for ann in self.annotations:
            if ann.get('pillar') == pillar or ann.get('ten_god') == ten_god:
                similar_days.append(ann)
        
        # 找同类下的反馈示例
        past_examples = []
        for ann in similar_days[:2]:
            past_examples.append(f"{ann['date']}({ann['pillar']})：{ann['feedback_excerpt']}")
        
        # 理论解读
        theory_entries = []
        
        # 十神
        tg = TEN_GOD_THEORY.get(ten_god, {})
        is_fav = get_five_element_from_stem(ds) in self.profile['favorite_elements']
        theory_entries.append({
            "label": f"十神·{ten_god}",
            "content": tg.get('essence', ''),
            "apply": tg.get('when_favorable' if is_fav else 'when_unfavorable', ''),
        })
        
        # 地支关系
        for rel in relations or ['平']:
            bt = BRANCH_RELATION_THEORY.get(rel, {})
            theory_entries.append({
                "label": f"地支·{rel}",
                "content": bt.get('essence', ''),
                "apply": bt.get(f'{EARTHLY_BRANCHES[db]}_combine', ''),
            })
        
        # 长生
        theory_entries.append({
            "label": f"十二长生·{stage_name}",
            "content": LIFE_STAGE_THEORY.get(stage_name, ''),
            "apply": f"辛金今日在{EARTHLY_BRANCHES[db]}为{stage_name}（力量系数{stage_power:.1f}），{'宜休养生息' if stage_power<0.4 else '正当其时，可有所作为' if stage_power>0.7 else '能量适中，按部就班'}",
        })
        
        return {
            "date": target_date,
            "pillar": pillar,
            "ten_god": ten_god,
            "relations": relations,
            "life_stage": (stage_name, stage_power),
            "theory": theory_entries,
            "past_examples": past_examples,
            "total_annotations": len(self.annotations),
        }


theory_engine = TheoryEngine()
