"""
个性化解读模块
基于用户已验证的命盘和人生经历，生成定制化的每日/每月/每年解读
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple
import math

from bazi_engine import (
    HEAVENLY_STEMS, EARTHLY_BRANCHES, STEM_ELEMENT, BRANCH_ELEMENT,
    get_day_stem_branch, get_hour_stem_branch, get_year_stem_branch,
    get_month_stem_branch, get_bazi_pillar_name, get_nayin,
    get_stem_relation, get_ten_god, get_branch_relation,
    get_five_element_from_stem, get_five_element_from_branch,
    get_hour_branch_from_time, calculate_daily_bazi,
    calculate_daily_score, compare_with_birth_chart
)
from user_profile import PROFILE, BIRTH_CHART, get_current_dayun
from dayun_weights import get_dayun_weight


# ============ 个性化解读模板 ============

class PersonalizedInterpreter:
    """个性化解读器"""
    
    def __init__(self):
        self.profile = PROFILE
        self.birth_chart = BIRTH_CHART
        
    def generate_daily_reading(self, target_date: date = None) -> Dict:
        """生成每日运势解读"""
        if target_date is None:
            target_date = date.today()
        
        # 计算当日八字 (辰时 8:00)
        daily_bazi = calculate_daily_bazi(target_date, 8, 0)
        current_dayun = get_current_dayun(target_date)
        
        # 计算评分
        day_stem = daily_bazi["day"]["stem"]
        day_branch = daily_bazi["day"]["branch"]
        birth_day_stem = self.birth_chart["day"]["stem"]
        birth_day_branch = self.birth_chart["day"]["branch"]
        
        score_result = calculate_daily_score(
            day_stem, day_branch,
            birth_day_stem, birth_day_branch,
            self.profile,
            dayun_weight=get_dayun_weight(current_dayun['name'])
        )
        
        # 与八字全面比较
        comparison = compare_with_birth_chart(daily_bazi, self.birth_chart)
        
        # 获取当前大运
        current_dayun = get_current_dayun(target_date)
        
        # 生成个性化解读
        interpretation = self._generate_interpretation(
            daily_bazi, score_result, comparison, current_dayun, target_date
        )
        
        # 获取时柱解读 (辰时)
        hour_reading = self._generate_hour_reading(daily_bazi)
        
        return {
            "date": target_date,
            "daily_bazi": daily_bazi,
            "score": score_result,
            "comparison": comparison,
            "interpretation": interpretation,
            "hour_reading": hour_reading,
            "current_dayun": current_dayun,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    
    def _generate_interpretation(self, daily_bazi, score_result, comparison, current_dayun, target_date) -> Dict:
        """生成综合解读"""
        day_stem = daily_bazi["day"]["stem"]
        day_branch = daily_bazi["day"]["branch"]
        
        # ---- 1. 今日总览 ----
        overview = self._generate_overview(score_result, daily_bazi, target_date)
        
        # ---- 2. 事业财运 ----
        career = self._generate_career_reading(daily_bazi, comparison, current_dayun)
        
        # ---- 3. 感情人际 ----
        relationship = self._generate_relationship_reading(daily_bazi, comparison)
        
        # ---- 4. 健康提示 ----
        health = self._generate_health_reading(daily_bazi, comparison)
        
        # ---- 5. 父母/家庭 ----
        family = self._generate_family_reading(daily_bazi, comparison)
        
        # ---- 6. 每日宜忌 ----
        advice = self._generate_daily_advice(daily_bazi, score_result, comparison)
        
        # ---- 7. 专属提醒 ----
        reminders = self._generate_reminders(daily_bazi, comparison, current_dayun, target_date)
        
        return {
            "overview": overview,
            "career": career,
            "relationship": relationship,
            "health": health,
            "family": family,
            "advice": advice,
            "reminders": reminders,
        }
    
    def _generate_overview(self, score_result, daily_bazi, target_date) -> Dict:
        """生成今日总览"""
        day_stem = daily_bazi["day"]["stem"]
        day_branch = daily_bazi["day"]["branch"]
        
        level = score_result["level"]
        score = score_result["score"]
        
        # 根据等级生成总评
        summaries = {
            "大吉": "今日能量充沛，诸事顺遂，宜把握机会大胆行动。",
            "吉": "今日运势不错，适合推进计划和重要事项。",
            "平": "今日能量平稳，宜按部就班，不宜冒进。",
            "不佳": "今日能量偏低，需多加留意外在环境的变化。",
            "谨慎": "今日需谨慎行事，重要决策最好延后。",
        }
        
        # 根据五行生成补充描述
        stem_elem = get_five_element_from_stem(day_stem)
        branch_elem = get_five_element_from_branch(day_branch)
        
        element_descriptions = {
            "木": "木气生发，宜创意和规划",
            "火": "火气上扬，注意情绪管理",
            "土": "土性敦厚，宜稳健行事",
            "金": "金气肃降，宜收尾和复盘",
            "水": "水势流动，宜灵活应变",
        }
        
        pillar_name = daily_bazi["day"]["name"]
        nayin = daily_bazi["day"]["nayin"]
        
        # 计算当天的农历日期 (简化)
        lunar_info = self._get_lunar_info(target_date)
        
        return {
            "summary": summaries.get(level, ""),
            "level": level,
            "score": score,
            "pillar": pillar_name,
            "nayin": nayin,
            "stem_element": stem_elem,
            "branch_element": branch_elem,
            "element_note": element_descriptions.get(stem_elem, ""),
            "lunar_info": lunar_info,
        }
    
    def _get_lunar_info(self, target_date: date) -> Dict:
        """获取农历信息 (简化版)"""
        # 简化农历计算
        lunar_month_map = {1: "正月", 2: "二月", 3: "三月", 4: "四月", 
                           5: "五月", 6: "六月", 7: "七月", 8: "八月",
                           9: "九月", 10: "十月", 11: "冬月", 12: "腊月"}
        
        # 公历月份近似农历 (不准确但够用)
        approx_lunar_month = target_date.month - 1
        if approx_lunar_month <= 0:
            approx_lunar_month = 12
        
        lunar_month_name = lunar_month_map.get(approx_lunar_month, "")
        
        # 公历日近似农历日 (仅为示意)
        lunar_day = target_date.day
        
        # 月相描述
        phase = ""
        if lunar_day <= 2:
            phase = "朔日·新月"
        elif lunar_day <= 7:
            phase = "蛾眉月"
        elif lunar_day <= 14:
            phase = "上弦月"
        elif lunar_day == 15:
            phase = "望日·满月"
        elif lunar_day <= 17:
            phase = "满月渐亏"
        elif lunar_day <= 22:
            phase = "下弦月"
        elif lunar_day <= 29:
            phase = "残月"
        else:
            phase = "晦日"
        
        return {
            "lunar_month": f"农历{lunar_month_name}",
            "lunar_day": f"第{lunar_day}日",
            "phase": phase,
        }
    
    def _generate_career_reading(self, daily_bazi, comparison, current_dayun) -> Dict:
        """生成事业财运解读"""
        day_stem = daily_bazi["day"]["stem"]
        day_branch = daily_bazi["day"]["branch"]
        birth_day_stem = self.birth_chart["day"]["stem"]
        
        ten_god = get_ten_god(birth_day_stem, day_stem)
        stem_elem = get_five_element_from_stem(day_stem)
        
        is_fav = stem_elem in self.profile["favorite_elements"]
        is_unfav = stem_elem in self.profile["unfavorable_elements"]
        
        # 十神解读
        ten_god_readings = {
            "正官": "正官日：利于与上级沟通、制度性事务。责任和规矩是今天的主题。",
            "七杀": "七杀日：压力较大，可能遇到挑战或强势的人。保持冷静，以柔克刚。",
            "正印": "正印日：学习、思考和接受支持的好日子。适合学习新知识、寻求帮助。",
            "偏印": "偏印日：灵感丰富，适合创意性工作和独立研究。注意不要太固执。",
            "比肩": "比肩日：有同行或朋友相助，但也可能有竞争。适合团队协作。",
            "劫财": "劫财日：人际关系活跃，可能有破财或应酬支出。注意金钱管理。",
            "食神": "食神日：心情愉悦，表达顺畅。适合展示才华、做分享和输出。",
            "伤官": "伤官日：想法很多，但容易言辞锋利得罪人。注意沟通方式。",
            "正财": "正财日：有稳定的财务机会，适合处理预算和结算类事务。",
            "偏财": "偏财日：有意外之财的机会，也可能有意外支出。不宜投机。",
        }
        
        # 地支影响解读
        branch_effects = []
        relations = comparison.get("day_vs_birth_day", {}).get("branch_relations", [])
        
        if "冲" in relations:
            branch_effects.append("日支相冲，今天工作环境可能有变动或突发状况，不宜做重大决策")
        if "合" in relations:
            branch_effects.append("日支相合，适合谈判、签约和重要沟通")
        if "刑" in relations:
            branch_effects.append("日支相刑，注意职场人际关系，避免卷入是非")
        if "害" in relations:
            branch_effects.append("日支相害，注意同事或合作伙伴的态度变化")
        
        # 大运影响
        dayun_effect = ""
        dayun_stem_elem = get_five_element_from_stem(current_dayun["stem"])
        dayun_branch_elem = get_five_element_from_branch(current_dayun["branch"])
        
        if current_dayun["name"] == "丙戌":
            dayun_effect = f"当前在丙戌大运(31-40岁)，火土运即将结束。2026年10月将换入乙酉大运，届时能量会大幅提升。当前处于过渡期，宜稳不宜急。"
        elif current_dayun["name"] == "乙酉":
            dayun_effect = f"当前在乙酉大运(41-50岁) 🔥 禄神到位，是你人生的黄金十年！身弱问题大幅缓解，事业和财运都有质的飞跃。大胆追求你想要的！"
        
        return {
            "ten_god": ten_god,
            "ten_god_reading": ten_god_readings.get(ten_god, ""),
            "is_favorable_day": is_fav,
            "is_unfavorable_day": is_unfav,
            "branch_effects": branch_effects,
            "dayun_effect": dayun_effect,
            "dayun_name": current_dayun["name"],
        }
    
    def _generate_relationship_reading(self, daily_bazi, comparison) -> Dict:
        """生成感情人际解读"""
        day_stem = daily_bazi["day"]["stem"]
        day_branch = daily_bazi["day"]["branch"]
        birth_day_stem = self.birth_chart["day"]["stem"]
        
        ten_god = get_ten_god(birth_day_stem, day_stem)
        
        # 感情相关十神解读
        love_related = ten_god in ["正官", "七杀", "正财", "偏财"]
        
        love_readings = {
            "正官": "正官出现，今天在人际关系中会比较注重规则和分寸。如果有感情机会，可能是通过正式场合或长辈介绍认识的。",
            "七杀": "七杀出现，今天可能会遇到比较有压迫感的人。保护好自己的边界，不要太快信任。",
            "正财": "正财出现，适合稳定的社交活动。感情上宜踏实，不宜冲动。",
            "偏财": "偏财出现，社交机会增多，但也可能遇到不靠谱的人。保持清醒判断。",
            "劫财": "劫财出现，注意人际关系中的竞争因素。朋友之间也可能有利益纠葛。",
            "食神": "食神出现，今天表达欲强，适合约会和交流。你的幽默和才华容易被看到。",
            "伤官": "伤官出现，言辞容易直接，注意不要无意中得罪人。感情上宜坦诚但别太尖锐。",
        }
        
        # 孤辰提示
        gu_chen_tip = "你是孤辰性格：独处充电、社交耗电。今天如果社交安排太多，记得给自己留一些独处时间恢复能量。"
        
        return {
            "ten_god_reading": love_readings.get(ten_god, "今天人际关系整体平稳，适合按自己的节奏来。"),
            "is_love_related_day": love_related,
            "gu_chen_tip": gu_chen_tip,
        }
    
    def _generate_health_reading(self, daily_bazi, comparison) -> Dict:
        """生成健康提示"""
        day_stem = daily_bazi["day"]["stem"]
        day_branch = daily_bazi["day"]["branch"]
        
        stem_elem = get_five_element_from_stem(day_stem)
        branch_elem = get_five_element_from_branch(day_branch)
        
        # 五行健康提示
        health_tips = []
        
        if stem_elem == "火" or branch_elem == "火":
            health_tips.append("火气偏旺：注意心脑血管和情绪管理，避免急躁。宜多喝水、深呼吸。")
        if stem_elem == "木" or branch_elem == "木":
            health_tips.append("木气偏旺：注意肝胆和消化系统，宜清淡饮食，适当运动疏解压力。")
        if stem_elem == "金" or branch_elem == "金":
            health_tips.append("金气偏旺：注意呼吸系统和皮肤，早晚温差大时注意保暖。")
        if stem_elem == "土" or branch_elem == "土":
            health_tips.append("土气偏旺：注意脾胃消化，七分饱为宜，少吃生冷。")
        if stem_elem == "水" or branch_elem == "水":
            health_tips.append("水气偏旺：注意肾脏和泌尿系统，避免受寒。")
        
        # 你自身易感问题
        personal_tips = [
            "你八字金弱火旺，整体要注意心火和情绪波动",
            "有孤辰+亡神，容易思虑过度影响睡眠",
        ]
        
        return {
            "tips": health_tips if health_tips else ["今日五行均衡，身体状态平稳，保持正常作息即可。"],
            "personal_tips": personal_tips,
        }
    
    def _generate_family_reading(self, daily_bazi, comparison) -> Dict:
        """生成父母/家庭相关提示"""
        day_stem = daily_bazi["day"]["stem"]
        
        # 父亲: 偏财(乙木=索引1)
        # 母亲: 印星(戊己土=索引4,5)
        
        stem_elem = get_five_element_from_stem(day_stem)
        
        family_notes = []
        
        # 木相关 (父亲)
        if day_stem in [0, 1]:  # 甲乙木
            if day_stem == 1:  # 乙木 = 偏财 = 父亲
                family_notes.append("今日乙木偏财日，与父亲能量有共振。可主动联系问候。")
            else:
                family_notes.append("今日甲木日，木气较旺，注意父亲健康方面的动态。")
        
        # 土相关 (母亲)
        if day_stem in [4, 5]:  # 戊己土
            family_notes.append("今日土日，与母亲能量有共鸣，适合问候或陪伴。")
        
        # 提醒年份
        current_year = date.today().year
        if current_year == 2027 and date.today().month >= 2:
            family_notes.append("⚠ 2027丁未年：父亲的健康年，伏吟时柱+木入墓库，建议关注肺部复查和认知状态。")
        elif current_year == 2029:
            family_notes.append("⚠ 2029己酉年：双酉克乙木，父亲的复查巩固年。")
        elif current_year == 2034:
            family_notes.append("⚠ 2034甲寅年：三寅克土，需关注母亲健康。")
        
        if not family_notes:
            family_notes.append("今日家庭能量平稳，没有特殊信号。平常心就好。")
        
        return {
            "notes": family_notes,
        }
    
    def _generate_daily_advice(self, daily_bazi, score_result, comparison) -> Dict:
        """生成每日宜忌和建议 - 针对上班族"""
        day_stem = daily_bazi["day"]["stem"]
        day_branch = daily_bazi["day"]["branch"]
        
        stem_elem = get_five_element_from_stem(day_stem)
        is_weekend = date.today().weekday() >= 5  # 周六日
        
        favorable_activities = []
        unfavorable_activities = []
        
        if stem_elem in self.profile["favorite_elements"]:
            # 喜用神日：可以主动
            if is_weekend:
                favorable_activities = [
                    "周末适当放松，补充睡眠",
                    "做一些自己感兴趣的事",
                    "如果愿意，可以约信任的朋友小聚",
                ]
            else:
                favorable_activities = [
                    "工作上可以主动推进重要任务",
                    "适合向领导汇报工作进展",
                    "处理积压的邮件和文档",
                    "利用午休时间散步、调节状态",
                ]
            unfavorable_activities = [
                "下班后过度加班透支自己",
                "随意答应同事的额外请求",
                "在情绪波动时做重要决定",
            ]
        elif stem_elem in self.profile["unfavorable_elements"]:
            # 忌神日：宜守不宜攻
            if is_weekend:
                favorable_activities = [
                    "在家独处充电，减少外出",
                    "整理房间、放松身心",
                    "做一顿好吃的犒劳自己",
                ]
            else:
                favorable_activities = [
                    "专注完成本职工作，减少额外揽活",
                    "午休时独处一会恢复能量",
                    "列好明日待办清单后准时下班",
                    "用温和的方式表达不同意见",
                ]
            unfavorable_activities = [
                "主动揽活或承诺额外工作量",
                "和同事/领导发生正面冲突",
                "下班后还沉浸在工作的情绪里",
                "冲动消费或做财务决定",
            ]
        else:
            favorable_activities = [
                "按计划过好今天",
                "做好手头的工作",
                "给自己一个放松的晚间时段",
            ]
            unfavorable_activities = [
                "过度承诺给别人",
                "在情绪不好时做决定",
            ]
        
        # 根据地支关系调整
        relations = comparison.get("day_vs_birth_day", {}).get("branch_relations", [])
        if "冲" in relations:
            unfavorable_activities.append("⚠ 今日相冲，重要沟通和文件签署尽量避开今天")
        if "合" in relations:
            favorable_activities.append("✓ 今日相合，适合推进需要协作的工作")
        
        return {
            "favorable": favorable_activities,
            "unfavorable": unfavorable_activities,
        }
    
    def _generate_reminders(self, daily_bazi, comparison, current_dayun, target_date) -> List[str]:
        """生成专属提醒 - 含特殊日子预警"""
        reminders = []
        
        day_branch = daily_bazi["day"]["branch"]
        birth_branch = self.birth_chart["day"]["branch"]  # 巳 = 5
        
        # ===== 特殊地支关系预警（基于你的日支巳） =====
        
        # 巳申合 (水局) - 合化泄身，容易累
        if day_branch == 8:  # 申
            reminders.append("🌊 【巳申合水日】今天你的日支巳与流日申相合化水。水泄金气，能量容易被合走，下午开始会明显感到累。建议：重要的事上午做，下午留时间给自己充电。")
        
        # 巳酉半合金局 - 禄神帮身，能量好日
        if day_branch == 9:  # 酉
            reminders.append("🔥 【巳酉半合金局日】禄神到位！今天你的日支巳与酉半合金局，身弱变强，能量充沛。适合推进重要事项，大胆表达自己。")
        
        # 巳午半会火局 - 加重忌神
        if day_branch == 6:  # 午
            reminders.append("🔥 【巳午半会火日】火势加重，注意心火和情绪波动。容易急躁或焦虑，做事前先深呼吸三次。")
        
        # 巳亥冲 - 冲击大
        if day_branch == 11:  # 亥
            reminders.append("⚡ 【巳亥冲日】今日与你的日支相冲，能量波动大。不宜做重大决定，注意身体健康（特别是心脑血管）。")
        
        # 巳寅相刑
        if day_branch == 2:  # 寅
            reminders.append("△ 【巳寅相刑日】注意人际关系中的小摩擦，言辞易伤人。能不说的就先不说。")
        
        # ===== 季节提醒 =====
        month = target_date.month
        if 3 <= month <= 5:
            reminders.append("🌱 春季木旺，你需要多用土金来平衡（穿米色/白色/金色，减少绿色/红色）")
        elif 6 <= month <= 8:
            reminders.append("☀️ 夏季火旺，注意防暑降心火，多补充水分，避免在烈日下久待")
        elif 9 <= month <= 11:
            reminders.append("🍂 秋季金旺，是你的好季节！能量充沛，适合大展拳脚")
        else:
            reminders.append("❄️ 冬季水旺，注意保暖，水泄金气，不宜过度劳累")
        
        # 大运交接提醒
        if current_dayun["name"] == "丙戌" and target_date.year == 2026:
            reminders.append("🔄 你正处于丙戌大运的最后阶段，2026年10月后将换入乙酉大运。当前宜积蓄能量，不要急着做重大变动。")
        
        # 生日提醒
        if target_date.month == 2 and target_date.day == 6:
            reminders.append("🎂 生日快乐！新的一岁，新的运势，加油！")
        
        # 月初/月末提醒
        if target_date.day <= 3:
            reminders.append("📅 月初，适合做本月规划和目标设定")
        elif target_date.day >= 27:
            reminders.append("📅 月末，适合复盘总结，整理收尾工作")
        
        if not reminders:
            reminders.append("没有特别提醒，享受今天的平静 ☀️")
        
        return reminders
    
    def _generate_hour_reading(self, daily_bazi) -> Dict:
        """生成辰时(8:00)特别解读 - 根据当天五行动态调整"""
        hour_stem = daily_bazi["hour"]["stem"]
        hour_branch = daily_bazi["hour"]["branch"]
        day_stem = daily_bazi["day"]["stem"]
        day_branch = daily_bazi["day"]["branch"]
        
        hour_name = daily_bazi["hour"]["name"]
        stem_elem = get_five_element_from_stem(hour_stem)
        
        birth_day_stem = self.birth_chart["day"]["stem"]
        hour_ten_god = get_ten_god(birth_day_stem, hour_stem)
        day_ten_god = get_ten_god(birth_day_stem, day_stem)
        
        # 动态描述 - 结合当日能量
        is_fav_day = get_five_element_from_stem(day_stem) in self.profile['favorite_elements']
        
        if is_fav_day:
            base = "今天整体能量对你有利，辰时适合趁势推进重要事项。"
        else:
            base = "今天整体能量偏弱，辰时适合从简单任务开始，逐步进入状态。"
        
        # 时干+日干的组合建议
        combos = {
            ("正官","正官"): "今日官星双双出现，规矩感强，适合处理制度性事务，注意不要被条条框框束缚。",
            ("食神","正官"): "今日食神生正官，表达和规则并存——适合通过沟通解决问题，但注意措辞。",
            ("伤官","正官"): "今日伤官见官，注意言辞不要过激，特别是和上级沟通时。",
            ("食神","食神"): "今日双食神，表达欲和创造力双双在线，适合做脑力工作和创意输出。",
            ("正印","正官"): "今日印星护官，学习效率高，适合早上先看资料再做事。",
        }
        combo_key = (hour_ten_god, day_ten_god)
        specific = combos.get(combo_key, f"今日时柱十神为{hour_ten_god}，日柱十神为{day_ten_god}，{'用神' if is_fav_day else '忌神'}日宜{'主动' if is_fav_day else '谨慎'}。")
        
        # 时柱纳音
        from bazi_engine import get_nayin
        nayin = get_nayin(hour_stem, hour_branch)
        
        return {
            "hour_name": hour_name,
            "hour_time": "07:00-09:00",
            "description": f"辰时(7-9点)时柱为{hour_name}（纳音{nayin}）。{base}",
            "ten_god": hour_ten_god,
            "ten_god_reading": specific,
            "element": stem_elem,
            "is_favorable": stem_elem in self.profile["favorite_elements"],
        }
    
    def generate_monthly_reading(self, year: int, month: int) -> Dict:
        """生成月度解读 - 带详细分项文字描述"""
        from calendar import monthrange
        
        first_day = date(year, month, 1)
        last_day = date(year, month, monthrange(year, month)[1])
        
        # 当月平均运势 (取月初、月中、月末三天)
        mid_day = date(year, month, 15) if monthrange(year, month)[1] >= 15 else first_day
        
        readings = []
        scores = []
        
        for d in [first_day, mid_day, last_day]:
            reading = self.generate_daily_reading(d)
            readings.append(reading)
            scores.append(reading["score"]["score"])
        
        avg_score = sum(scores) / len(scores)
        
        # 当月干支
        year_stem, year_branch = get_year_stem_branch(year)
        month_stem, month_branch = get_month_stem_branch(year_stem, month - 1)
        month_pillar = get_bazi_pillar_name(month_stem, month_branch)
        month_stem_elem = get_five_element_from_stem(month_stem)
        month_branch_elem = get_five_element_from_branch(month_branch)
        
        current_dayun = get_current_dayun(first_day)
        
        # 当月关键日期
        key_dates = self._find_key_dates(year, month, current_dayun)
        
        
        # ---- 分项详细解读 ----
        details = self._generate_monthly_details(year, month, month_stem, month_branch, month_pillar, avg_score, current_dayun)
        
        # ---- 工作层面的针对性建议 ----
        work_advice = self._generate_work_advice(month_stem, month_branch, month, current_dayun)
        
        return {
            "year": year,
            "month": month,
            "month_pillar": month_pillar,
            "avg_score": round(avg_score, 1),
            "level": self._score_to_level(avg_score),
            "readings": readings,
            "key_dates": key_dates,
            "current_dayun": current_dayun,
            "details": details,
            "work_advice": work_advice,
        }
    
    def _generate_monthly_details(self, year, month, month_stem, month_branch, month_pillar, avg_score, dayun):
        """生成月度各分项详细解读"""
        stem_elem = get_five_element_from_stem(month_stem)
        branch_elem = get_five_element_from_branch(month_branch)
        is_fav = stem_elem in self.profile["favorite_elements"]
        is_unfav = stem_elem in self.profile["unfavorable_elements"]
        
        # ---- 整体 ----
        if is_fav:
            overview = f"本月月柱「{month_pillar}」，天干{stem_elem}为喜用神，整体能量对您有利。工作推进相对顺畅，适合主动出击。"
        elif is_unfav:
            overview = f"本月月柱「{month_pillar}」，天干{stem_elem}为忌神，整体能量偏弱。宜以守为主，减少不必要的变动和开支。"
        else:
            overview = f"本月月柱「{month_pillar}」，五行能量中性，运势平稳。按部就班即可，不宜大进大退。"
        
        # ---- 事业 ----
        career = f"本月天干为「{HEAVENLY_STEMS[month_stem]}」({stem_elem})，"
        if stem_elem in self.profile["favorite_elements"]:
            career += "与您喜用神相符，工作上思路清晰，执行力强。适合推进重点任务、与上级沟通、争取资源。"
        elif stem_elem in self.profile["unfavorable_elements"]:
            career += "为忌神，工作上容易感到阻力或压力。建议多一事不如少一事，专注手头工作，不宜主动求变。"
        else:
            career += "能量中性。宜保持现有节奏，按计划推进即可。"
        
        # ---- 财运 ----
        wealth = "本月"
        if is_fav:
            wealth += f"财运向好，正财收入稳定。如有投资或理财计划，可在月中的吉日进行操作。避免冲动消费即可。"
        elif is_unfav:
            wealth += f"财运偏弱，需注意不必要的开支和冲动消费。不宜投资、借钱给他人或参与高风险项目。"
        else:
            wealth += f"财运平稳，收入支出大致平衡，没有大的财务波动。"
        
        # ---- 健康 ----
        health = f"本月五行偏{stem_elem}。"
        if stem_elem == "火":
            health += "注意心火旺盛导致失眠、焦虑。多喝水、少熬夜，午间适当休息。"
        elif stem_elem == "木":
            health += "注意肝胆和消化系统，饮食宜清淡。春季尤需注意过敏和皮肤问题。"
        elif stem_elem == "金":
            health += "注意呼吸系统和皮肤保养。秋季温差大时注意保暖。"
        elif stem_elem == "土":
            health += "注意脾胃消化，少吃生冷油腻。七分饱为宜。"
        elif stem_elem == "水":
            health += "注意保暖防寒，肾脏和泌尿系统需留意。"
        health += "你八字金弱，整体要注意劳逸结合，避免过度消耗。"
        
        # ---- 父母/家庭 ----
        if month_stem in [0, 1]:  # 甲乙木
            family = "本月木气偏旺，与父亲能量有共振。建议主动问候，关注父亲身体状况。"
        elif month_stem in [4, 5]:  # 戊己土
            family = "本月土气偏旺，与母亲能量有共鸣。适合多陪伴家人或安排家庭聚餐。"
        else:
            family = "本月家庭能量平稳，没有特殊信号。保持日常联系即可。"
        
        # 特殊年份提醒
        if year == 2026 and month >= 10:
            family += " ⚠ 你即将进入乙酉大运，10月后能量格局有大变化，注意父亲在此期间的身体适应。"
        elif year == 2027:
            family += " ⚠ 2027丁未年，父亲需重点关注。建议上半年做一次全面体检，尤其肺部CT和认知评估。"
        
        # ---- 感情/姻缘 ----
        love = "本月"
        if month_stem in [2, 3]:  # 丙丁火
            love += "正官/七杀能量偏强。如有伴侣，注意沟通方式，避免因工作压力迁怒对方。如单身，有机会通过工作场合认识新人。"
        elif month_stem in [0, 1]:  # 甲乙木
            love += "偏财/正财能量偏强。社交机会增多，但也容易遇到不靠谱的人和事。保持清醒，宁缺毋滥。"
        elif month_stem in [6, 7]:  # 庚辛金
            love += "比劫帮身，你在感情中会更有安全感。适合主动表达想法和需求。"
        elif month_stem in [4, 5]:  # 戊己土
            love += "印星护身，感情上偏理性。适合沉淀和思考自己在感情中的真正需求。"
        else:
            love += "感情方面没有特别的信号。按自己的节奏来就好。"
        
        # ---- 注意事项 ----
        warnings = []
        relations_with_birth = get_branch_relation(month_branch, self.birth_chart["month"]["branch"])
        if "冲" in relations_with_birth:
            warnings.append("⚠ 本月地支与您月支相冲，易有工作环境的变动或人际关系的波动，重要决策尽量避开。")
        if "刑" in relations_with_birth:
            warnings.append("△ 本月地支与您月支相刑，注意职场人际关系，避免卷入是非。")
        if "合" in relations_with_birth:
            warnings.append("✓ 本月地支与您月支相合，人缘佳，合作事宜易成。")
        
        # 大运交接提醒
        if dayun["name"] == "丙戌" and year == 2026 and month >= 9:
            warnings.append("🔥 你即将在10月换入乙酉大运！这是你人生的黄金十年，能量格局将发生根本性变化。建议在换运前做好职业规划，迎接新阶段。")
        
        if not warnings:
            warnings.append("本月没有特别的外部冲刑信号，平稳度过的概率较大。")
        
        return {
            "overview": overview,
            "career": career,
            "wealth": wealth,
            "health": health,
            "family": family,
            "love": love,
            "warnings": warnings,
        }
    
    def _generate_work_advice(self, month_stem, month_branch, month, dayun):
        """生成针对上班族的实用工作建议"""
        advice_list = []
        
        # 根据月柱给出实用建议
        stem_elem = get_five_element_from_stem(month_stem)
        
        if stem_elem in self.profile["favorite_elements"]:
            advice_list.append("✅ 本月能量充沛，适合在现有岗位上争取更多主动权和能见度")
            advice_list.append("   • 可以主动向领导汇报工作成果")
            advice_list.append("   • 适合参与重要项目或跨部门协作")
            advice_list.append("   • 有跳槽/换岗想法的话，可以在月中吉日行动")
        elif stem_elem in self.profile["unfavorable_elements"]:
            advice_list.append("⚠ 本月能量偏低，建议以稳为主，减少不必要的变动")
            advice_list.append("   • 专注完成本职工作，减少额外揽活")
            advice_list.append("   • 注意控制情绪，避免与同事/领导发生冲突")
            advice_list.append("   • 不适合在本月做跳槽或重大职业决策")
        else:
            advice_list.append("🔶 本月能量平稳，按部就班推进工作即可")
            advice_list.append("   • 适合做日常性、重复性的积累工作")
            advice_list.append("   • 可以利用碎片时间学习充电")
        
        # 大运交接期特别建议
        if dayun["name"] == "丙戌" and month >= 9:
            advice_list.append("🔥 【特别提醒】10月换乙酉大运，这是你人生的关键转折点。建议提前梳理职业规划，准备好迎接新的能量周期。")
        
        return advice_list
    
    def _find_key_dates(self, year: int, month: int, current_dayun: Dict = None) -> List[Dict]:
        """找到当月关键日期（高分日/低分日）"""
        from calendar import monthrange
        
        dayun_weight = get_dayun_weight(current_dayun['name']) if current_dayun else 0
        
        num_days = monthrange(year, month)[1]
        scored_days = []
        
        for day in range(1, num_days + 1):
            d = date(year, month, day)
            ds, db = get_day_stem_branch(d)
            birth_ds = self.birth_chart["day"]["stem"]
            birth_db = self.birth_chart["day"]["branch"]
            
            sr = calculate_daily_score(ds, db, birth_ds, birth_db, self.profile, dayun_weight=dayun_weight)
            scored_days.append({
                "date": d,
                "score": sr["score"],
                "level": sr["level"],
                "pillar": get_bazi_pillar_name(ds, db),
            })
        
        # 找出高分日(>=75)和低分日(<=30)
        good_days = [d for d in scored_days if d["score"] >= 75]
        bad_days = [d for d in scored_days if d["score"] <= 35]
        
        return {
            "good_days": good_days[:5],  # 最多5个
            "bad_days": bad_days[:5],
            "all": scored_days,
        }
    
    def generate_yearly_reading(self, year: int) -> Dict:
        """生成年度解读 - 带详细分项文字描述"""
        # 年柱
        year_stem, year_branch = get_year_stem_branch(year)
        year_pillar = get_bazi_pillar_name(year_stem, year_branch)
        
        birth_day_stem = self.birth_chart["day"]["stem"]
        year_ten_god = get_ten_god(birth_day_stem, year_stem)
        stem_elem = get_five_element_from_stem(year_stem)
        branch_elem = get_five_element_from_branch(year_branch)
        is_fav_year = stem_elem in self.profile["favorite_elements"]
        
        # 年度得分
        monthly_scores = []
        for m in range(1, 13):
            mr = self.generate_monthly_reading(year, m)
            monthly_scores.append(mr["avg_score"])
        avg_year_score = sum(monthly_scores) / len(monthly_scores)
        
        current_dayun = get_current_dayun(date(year, 6, 15))
        keywords = self._get_year_keywords(year, year_pillar, current_dayun)
        
        # 月运概览
        monthly_overview = []
        for m in range(1, 13):
            mr = self.generate_monthly_reading(year, m)
            monthly_overview.append({
                "month": m,
                "score": mr["avg_score"],
                "level": mr["level"],
                "pillar": mr["month_pillar"],
                "details": mr.get("details", {}),
            })
        
        # ---- 年度分项详细解读 ----
        details = self._generate_yearly_details(year, year_stem, year_branch, year_pillar, is_fav_year, stem_elem, current_dayun, keywords)
        
        return {
            "year": year,
            "year_pillar": year_pillar,
            "year_ten_god": year_ten_god,
            "stem_element": stem_elem,
            "branch_element": branch_elem,
            "is_favorable_year": is_fav_year,
            "avg_score": round(avg_year_score, 1),
            "level": self._score_to_level(avg_year_score),
            "keywords": keywords,
            "current_dayun": current_dayun,
            "monthly_overview": monthly_overview,
            "details": details,
        }
    
    def _generate_yearly_details(self, year, year_stem, year_branch, year_pillar, is_fav, stem_elem, dayun, keywords):
        """生成年度各分项详细解读"""
        # ---- 整体 ----
        if is_fav:
            overview = f"{year}年为「{year_pillar}」年，天干{stem_elem}为喜用神，整体运势向好。加上当前在{dayun['name']}大运，能量配合得当，是值得把握的一年。"
        else:
            overview = f"{year}年为「{year_pillar}」年，天干{stem_elem}为忌神，整体运势偏保守。但大运{dayun['name']}有一定的化解作用，不至于太差。"
        
        if isinstance(keywords, dict) and 'message' in keywords:
            overview += f" 年度主题：{keywords['message']}"
        
        # ---- 事业 ----
        if is_fav:
            career = f"今年天干为喜用神，事业上相对顺遂。"
            if year == 2028:
                career += " 戊申年，土金齐到，是跳槽、晋升、启动大项目的最佳窗口。建议提前做好规划，大胆争取。"
            elif year == 2029:
                career += " 己酉年，禄神归位，是你职业生涯的巅峰之年。适合承担更大责任、争取更高职位。"
            else:
                career += " 适合在现有岗位上稳步推进，争取更多能见度和主动权。"
        else:
            career = f"今年天干为忌神，工作上需以稳为主。避免主动求变、冲动跳槽。专注做好本职工作，减少不必要的冲突和消耗。"
        
        # ---- 财运 ----
        if is_fav:
            wealth = f"今年财运整体向好。正财收入稳定，偏财方面可以关注理财机会，但不建议投机。"
        else:
            wealth = f"今年财运偏紧，需注意节约开支。不宜投资、借贷或参与高风险项目。"
        
        # ---- 健康 ----
        health = f"今年五行偏{stem_elem}。"
        if stem_elem == "火":
            health += "注意心脑血管和情绪管理。你八字火为忌神，火旺的年份容易焦虑、失眠，需要主动调节。"
        elif stem_elem == "金":
            health += "金为喜用神，今年身体状态整体不错。注意呼吸系统的保养即可。"
        elif stem_elem == "土":
            health += "土为喜用神，脾胃功能会有所改善。注意不要暴饮暴食。"
        elif stem_elem == "水":
            health += "水泄金气，注意不要过度劳累。肾脏和泌尿系统需关注。"
        elif stem_elem == "木":
            health += "木为忌神，注意肝胆和情绪管理。压力大时多做放松训练。"
        health += " 你八字金弱，整体要注意劳逸结合。"
        
        # ---- 父母 ----
        if year == 2026:
            family = "今年是丙戌运最后一年，10月换乙酉运。父母方面：父亲在2027年需重点关注，今年建议建立健康档案基线。"
        elif year == 2027:
            family = "⚠ 2027丁未年，父亲健康的关键年。建议年初做全面体检（肺部CT+认知评估），提前布局医疗资源。"
        elif year == 2029:
            family = "⚠ 2029己酉年，父亲健康的复查巩固年。双酉克乙木，不能放松警惕。"
        elif year == 2034:
            family = "⚠ 2034甲寅年，三寅克土，需重点关注母亲健康。"
        else:
            family = "今年家庭方面没有特殊信号，保持日常联系和定期体检即可。"
        
        # ---- 感情 ----
        if year == 2028 or year == 2029:
            love = "今年你在乙酉大运中，身弱问题大幅缓解，感情上也开始有能力承接一段健康的关系。可以保持开放的心态。"
        elif year == 2026:
            love = "今年是过渡年，感情上不必强求。先处理好自己的状态，等换运后再看缘分。"
        elif year == 2027:
            love = "换运过渡期，感情上以整理旧情结为主。新缘分可能在2028年后出现。"
        else:
            love = "今年感情方面没有特别信号。保持平常心即可。"
        
        # ---- 特别提醒 ----
        warnings = []
        if dayun["name"] == "丙戌" and year == 2026:
            warnings.append("🔥 2026年10月是你人生的关键转折点——丙戌运结束，乙酉大运开启。这是你第一次进入禄神大运，身弱问题将大幅缓解。建议提前做好职业和人生的规划。")
        if year in [2027, 2029]:
            warnings.append(f"⚠ {year}年需关注父亲健康，详见父母部分的提醒。")
        
        return {
            "overview": overview,
            "career": career,
            "wealth": wealth,
            "health": health,
            "family": family,
            "love": love,
            "warnings": warnings,
        }
    
    def _get_year_keywords(self, year: int, year_pillar: str, dayun: Dict) -> List[str]:
        """获取年度关键词"""
        keywords = []
        
        # 根据特定年份定制
        year_data = {
            2026: {
                "keywords": ["过渡", "积蓄", "等待", "转折"],
                "message": "2026年是过渡之年。上半年仍在丙戌运末期，10月后换入乙酉大运。前半段宜稳守，后半段逐步发力。"
            },
            2027: {
                "keywords": ["适应", "铺垫", "观察", "父亲健康"],
                "message": "2027丁未年，换运后第一年。慢慢适应新大运的能量，不要急。注意父亲健康。"
            },
            2028: {
                "keywords": ["突破", "进取", "跳跃", "🎯"],
                "message": "2028戊申年，土金大吉之年！申金劫财帮身，适合跳槽、晋升、大项目。事业的转折点！"
            },
            2029: {
                "keywords": ["巅峰", "收获", "爆发", "🔥"],
                "message": "2029己酉年，酉金禄神到位，是乙酉运的巅峰之年！大胆追求目标，这是你发光的一年。"
            },
            2030: {
                "keywords": ["巩固", "稳定", "回报", "✅"],
                "message": "2030庚戌年，延续好运。要注意戌未刑带来的变动，但总体向好。适合把前两年的成果落地。"
            },
        }
        
        if year in year_data:
            keywords = year_data[year]
        else:
            # 通用判断
            stem_elem = get_five_element_from_stem(get_year_stem_branch(year)[0])
            if stem_elem in self.profile["favorite_elements"]:
                keywords = {"keywords": ["大吉", "进取", "收获"], 
                           "message": f"{year}年整体运势向好，宜积极进取。"}
            else:
                keywords = {"keywords": ["守成", "谨慎", "调整"],
                           "message": f"{year}年需以守为主，不宜冒进。"}
        
        return keywords
    
    def _score_to_level(self, score: float) -> str:
        """分数转等级"""
        if score >= 80:
            return "大吉"
        elif score >= 65:
            return "吉"
        elif score >= 45:
            return "平"
        elif score >= 30:
            return "不佳"
        else:
            return "谨慎"


# 全局解读器实例
interpreter = PersonalizedInterpreter()
