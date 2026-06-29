"""
替换 server.py 中的流日页面内容生成部分
将旧的顺序式布局改为 象·数·理·体·用 组织
"""
import re

def main():
    with open('server.py', 'r') as f:
        code = f.read()
    
    start_marker = "content = f'''\n        <div class=\"date-nav\">"
    end_marker = "        self._send_html(self._page(content, 'home'))"
    
    s = code.find(start_marker)
    e = code.find(end_marker)
    
    if s < 0 or e < 0:
        print("ERROR: markers not found")
        return
    
    # 新内容模板
    new_content = """\
        lev_class = LEVEL_CLASSES.get(s['level'], 'ping')
        
        prev_d = target_date - timedelta(days=1)
        next_d = target_date + timedelta(days=1)
        
        # ===== ① 象 — 今日之象 =====
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
        <div class="score-label">{s['level']}</div></div>
        <div class="score-info">
        <div class="score-pillar">{r['daily_bazi']['day']['name']} · {r['daily_bazi']['day']['nayin']}</div>
        <div class="score-element">天干{o['stem_element']} · 地支{o['branch_element']} · 十神{c['ten_god']}</div>
        </div></div>
        
        <div class="card"><div class="card-header"><span class="card-icon">📋</span><span class="card-title">今日概况</span></div>
        <p class="card-text">{o['summary']}</p>
        <p class="card-text card-sub">{o.get('element_note','')}</p></div>
        
        <div class="card"><div class="card-header"><span class="card-icon">✅</span><span class="card-title">宜忌</span></div>
        <div class="advice-col">
        <div class="advice-good"><h4>✅ 宜</h4><ul>'''
        for item in adv['favorable'][:5]:
            content += f'<li>{item}</li>'
        content += '</ul></div><div class="advice-bad"><h4>❌ 不宜</h4><ul>'
        for item in adv['unfavorable'][:5]:
            content += f'<li>{item}</li>'
        content += '</ul></div></div></div>'
        
        # 计划
        today_plans = get_plans_by_date(target_date.isoformat())
        if today_plans:
            content += '<div class="card card-highlight"><div class="card-header"><span class="card-icon">📌</span><span class="card-title">今日安排</span></div>'
            for plan in today_plans:
                content += f'<p class="card-text">• <strong>{plan["title"]}</strong>'
                if plan.get('description'):
                    content += f'：{plan["description"]}'
                content += f' <span class="tag" style="font-size:11px">{plan.get("category","")}</span></p>'
            content += '</div>'
        
        # ===== ② 数 — 今日之数 =====
        content += f'<div class="section-label"><span class="section-tag">数</span><span>今天的八字力场和参数</span></div>'
        
        try:
            vf = force_engine.get_visual_forces(target_date)
            bars_html = ''
            for b in vf['bars']:
                pct = min(100, abs(b['value']) * 8)
                bar_cls = 'force-good' if b['value'] > 0 else 'force-bad' if b['value'] < 0 else 'force-neutral'
                val_cls = 'pos' if b['value'] > 0 else 'neg' if b['value'] < 0 else ''
                sign = '+' if b['value'] > 0 else ''
                bars_html += f'<div class="force-bar"><span class="force-label">{b["label"]}</span><div class="force-track"><div class="force-fill {bar_cls}" style="width:{pct}%"></div></div><span class="force-value {val_cls}">{sign}{b["value"]}</span></div>'
            ls_html = ''
            for ls in vf['life_stages'][:4]:
                stage_cls = 'stage-strong' if ls['power'] >= 0.7 else 'stage-weak' if ls['power'] <= 0.3 else 'stage-mid'
                ls_html += f'<div class="life-item"><span>{ls["position"]}</span><span class="life-stage {stage_cls}">{ls["stage"]}({ls["power"]:.1f})</span></div>'
            int_html = ''
            for it in vf['interactions'][:3]:
                int_html += f'<p class="card-text card-sub">• {it["desc"]} ({it["force"]:+d})</p>'
            content += f'''
            <div class="card"><div class="card-header"><span class="card-icon">⚡</span><span class="card-title">力场分析</span><span class="card-badge">{vf["total_score"]}分</span></div>
            <p class="card-text">{vf["summary"]}</p>
            <div style="margin:12px 0">{bars_html}</div>
            <details><summary style="font-size:13px;color:#888;cursor:pointer">▼ 十二长生</summary><div class="life-grid">{ls_html}</div></details>
            <details><summary style="font-size:13px;color:#888;cursor:pointer;margin-top:8px">▼ 地支交互力</summary><div style="margin-top:6px">{int_html}</div></details>
            </div>'''
        except Exception as e:
            content += f'<!-- force error: {e} -->'
        
        # ===== ③ 理 — 经典之理 =====
        content += f'<div class="section-label"><span class="section-tag">理</span><span>经典理论如何解释今天的参数</span></div>'
        
        try:
            td = theory_engine.get_today_theory(target_date)
            th_html = ''
            for t in td['theory'][:4]:
                th_html += f'<p class="card-text" style="margin-bottom:10px"><strong>{t["label"]}</strong><br><span class="card-sub">{t["content"]}</span><br><span style="font-size:14px">{t["apply"]}</span></p>'
            pe_html = ''
            for ex in td['past_examples'][:2]:
                pe_html += f'<p class="card-text card-sub">• {ex}</p>'
            det = ''
            if pe_html:
                det = '<details><summary style="font-size:13px;color:#888;cursor:pointer">▼ 往期同类日参考</summary>' + pe_html + '</details>'
            content += f'''
            <div class="card" style="background:#f5f0eb">
            <div class="card-header"><span class="card-icon">📜</span><span class="card-title">{td["pillar"]}理数解析</span></div>
            {th_html}
            {det}
            </div>'''
        except Exception as e:
            content += f'<!-- theory error: {e} -->'
        
        # 昨日回顾
        yesterday = target_date - timedelta(days=1)
        y_fb = get_feedback_by_date(yesterday.isoformat())
        if y_fb and y_fb.get('actual_feedback'):
            y_text = y_fb['actual_feedback'][:150]
            y_score = y_fb.get('prediction_score', '')
            y_acc = y_fb.get('accuracy_rating', 0) or 0
            y_stars = '★'*y_acc + '☆'*(5-y_acc)
            _, y_branch = get_day_stem_branch(yesterday)
            db = r['daily_bazi']['day']['branch']
            ny_rel = get_branch_relation(db, y_branch)
            ny_s = '、'.join(ny_rel) if ny_rel else '平'
            today_e = EARTHLY_BRANCHES[db]
            yest_e = EARTHLY_BRANCHES[y_branch]
            rel_m = {'合':'汇聚','冲':'对冲','刑':'纠结','害':'暗耗','三合':'共振','自刑':'内耗'}
            expl = [rel_m.get(r,r) for r in (ny_rel or ['平'])]
            explain = '→'.join(expl)
            story = ''
            if y_branch == 9 and db == 10:
                story = '昨天禄神日，今天转戌相害，不要因为昨天状态好就硬撑。'
            elif db == 9:
                story = '今天是你的禄神日！能量回升。'
            content += f'''
            <div class="card" style="background:#f5f0eb">
            <div class="card-header"><span class="card-icon">📖</span><span class="card-title">印证·昨日回顾</span></div>
            <p class="card-text card-sub">昨日({yesterday.strftime("%m月%d日")})「{y_text}」</p>
            <p class="card-text card-sub">准确度: {y_stars} | 预测{y_score}分</p>
            <p class="card-text" style="margin-top:6px">📌 昨日地支「{yest_e}」→ {ny_s} → 今日地支「{today_e}」：{explain}</p>
            <p class="card-text" style="background:#fff;padding:12px;border-radius:8px;margin:4px 0">💡 {story}</p></div>'''
        
        # 智慧库
        try:
            wisdom_engine.refresh_wisdom()
            tw = wisdom_engine.get_wisdom_for_today(target_date)
            if tw.get('matches'):
                content += f'<div class="card" style="background:#f5f0eb"><div class="card-header"><span class="card-icon">🧠</span><span class="card-title">智慧库</span><span class="card-badge">{tw["total_feedback_days"]}天</span></div>'
                for m in tw['matches']:
                    content += f'<p class="card-text" style="margin-bottom:6px">• {m["wisdom"]}</p>'
                content += '</div>'
        except Exception:
            pass
        
        # ===== ④ 体 — 各领域 =====
        content += f'<div class="section-label"><span class="section-tag">体</span><span>各领域的当天表现</span></div>
        
        <div class="card card-highlight"><div class="card-header"><span class="card-icon">🔄</span><span class="card-title">大运 · {reading['current_dayun']['name']}</span>
        <span class="card-badge">{reading['current_dayun']['age']}岁</span></div>
        <p class="card-text">{c['dayun_effect']}</p></div>
        
        <div class="card"><div class="card-header"><span class="card-icon">💼</span><span class="card-title">事业</span></div>
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
        
        <div class="card"><div class="card-header"><span class="card-icon">🏥</span><span class="card-title">健康</span></div>'''
        for tip in h['tips']:
            content += f'<p class="card-text">• {tip}</p>'
        content += '<details class="card-details"><summary style="font-size:13px;color:#888;cursor:pointer">▼ 个人体质说明</summary>'
        for tip in h['personal_tips']:
            content += f'<p class="card-text card-sub">• {tip}</p>'
        content += '</details></div>'
        
        content += f'''
        <div class="card"><div class="card-header"><span class="card-icon">👨‍👩‍👧</span><span class="card-title">家庭</span></div>'''
        for note in fam['notes']:
            content += f'<p class="card-text">• {note}</p>'
        content += '</div>'
        
        # ===== ⑤ 用 — 今日之用 =====
        content += f'<div class="section-label"><span class="section-tag">用</span><span>今天你该怎么做</span></div>
        
        <div class="card card-reminder"><div class="card-header"><span class="card-icon">🔔</span><span class="card-title">提醒</span></div>'''
        for reminder in rem:
            content += f'<p class="card-text">• {reminder}</p>'
        content += '</div>'
        
        content += f'''
        <div class="card"><div class="card-header"><span class="card-icon">🌅</span><span class="card-title">辰时 (7-9点)</span></div>
        <p class="card-text">{hr["description"]}</p>
        <p class="card-text card-sub">{hr["ten_god_reading"]}</p></div>
        
        <div class="card card-feedback">
        <div class="card-header"><span class="card-icon">📝</span><span class="card-title">记录今日之象</span></div>'''
        
        if fb:
            fb_show = (fb.get('actual_feedback') or '')[:150]
            content += f'<div class="feedback-exists"><p>✅ 今日已记录</p>'
            if fb_show:
                content += f'<p class="card-sub">你写了: {fb_show}{"…" if len(fb.get("actual_feedback","") or "")>150 else ""}</p>'
            content += f'<button onclick="var f=document.getElementById(\'feedback-form\');if(f)f.classList.remove(\'hidden\');" class="btn btn-sm">✏️ 修改</button></div>'
        
        content += f'''
        <form id="feedback-form" method="post" class="{"hidden" if fb else ""}" onsubmit="return submitFeedback(event)">
        <input type="hidden" name="date" value="{target_date.isoformat()}">
        <input type="hidden" name="prediction_score" value="{s["score"]}">
        <input type="hidden" name="prediction_level" value="{s["level"]}">
        <textarea name="actual_feedback" rows="3" placeholder="今天发生了什么？写下来充实你的命理注疏…" class="feedback-input"></textarea>
        <div class="feedback-ratings">
        <div class="rating-group"><label>感受</label>
        <div class="stars" data-name="actual_rating">
        <span class="star" data-value="1" onclick="setRating(this)">☆</span>
        <span class="star" data-value="2" onclick="setRating(this)">☆</span>
        <span class="star" data-value="3" onclick="setRating(this)">☆</span>
        <span class="star" data-value="4" onclick="setRating(this)">☆</span>
        <span class="star" data-value="5" onclick="setRating(this)">☆</span>
        </div></div>
        <div class="rating-group"><label>准度</label>
        <div class="stars" data-name="accuracy_rating">
        <span class="star" data-value="1" onclick="setRating(this)">☆</span>
        <span class="star" data-value="2" onclick="setRating(this)">☆</span>
        <span class="star" data-value="3" onclick="setRating(this)">☆</span>
        <span class="star" data-value="4" onclick="setRating(this)">☆</span>
        <span class="star" data-value="5" onclick="setRating(this)">☆</span>
        </div></div></div>
        <button type="submit" class="btn btn-primary">提交 → 充实智慧库</button>
        </form></div>'''
        """
    
    # 执行替换
    new_code = code[:s] + new_content + code[e:]
    
    with open('server.py', 'w') as f:
        f.write(new_code)
    
    print("✅ 替换完成")
    print(f"  原内容: {e-s} 字符")
    print(f"  新内容: {len(new_content)} 字符")

if __name__ == '__main__':
    main()
