#!/Users/luosichu/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
"""
竞品分析日报 · 飞书推送脚本 v2
从HTML报告DATA对象提取数据，生成有内容的飞书消息卡片
"""

import json
import os
import re
import sys
from datetime import datetime, date

# ===== 配置区 =====
WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/58b32bbe-8ed9-47a0-b681-d4a635d93f04"
REPORT_PATH = os.path.expanduser("~/Desktop/竞品分析日报.html")
DAILY_CRON_SCRIPT = os.path.expanduser("~/Desktop/daily_cron.sh")

# ===== 发送函数 =====
try:
    import requests
except ImportError:
    print("❌ 需要安装 requests 库: pip3 install requests")
    sys.exit(1)


def extract_all_data(html_path):
    """从HTML中提取所有结构化数据"""
    if not os.path.exists(html_path):
        return None, f"报告文件不存在: {html_path}"
    
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    today = date.today()
    week_cn = ['一','二','三','四','五','六','日'][today.weekday()]
    
    # 提取更新时间
    update_match = re.search(r'上次更新：<strong>([^<]+)</strong>', content)
    update_time = update_match.group(1) if update_match else "未知"
    
    regions_data = {}
    
    # 提取每个地区的DATA对象
    for region_var, region_info in [
        ('DATA.jp', {'key': 'jp', 'name': '日本', 'flag': '🇯🇵'}),
        ('DATA.us', {'key': 'us', 'name': '欧美', 'flag': '🌎'}),
        ('DATA.hktw', {'key': 'hktw', 'name': '港台', 'flag': '🏯'}),
    ]:
        start = content.find(f'{region_var} = {{')
        if start == -1:
            continue
        depth = 1
        pos = start + len(f'{region_var} = {{')
        while depth > 0 and pos < len(content):
            if content[pos] == '{': depth += 1
            elif content[pos] == '}': depth -= 1
            if depth > 0: pos += 1
        data_block = content[start:pos+1]
        
        region_data = {'info': region_info}
        
        # 提取Hot Topics Top5
        top5_match = re.search(r'top5:\s*\[(.*?)\]', data_block, re.DOTALL)
        if top5_match:
            top5_text = top5_match.group(1)
            games = re.findall(r'game:\s*"([^"]+)"', top5_text)
            contents = re.findall(r'content:\s*"([^"]+)"', top5_text)
            engagements = re.findall(r'engagement:\s*"([^"]+)"', top5_text)
            links = re.findall(r'link:\s*"([^"]+)"', top5_text)
            
            region_data['top5'] = []
            for i in range(min(5, len(games))):
                entry = {
                    'game': games[i] if i < len(games) else '',
                    'content': contents[i][:80] if i < len(contents) else '',
                    'engagement': engagements[i] if i < len(engagements) else '',
                    'link': links[i] if i < len(links) else '',
                }
                region_data['top5'].append(entry)
        
        # 提取Trending Topics
        trending_match = re.search(r'trending:\s*\[(.*?)\]', data_block, re.DOTALL)
        if trending_match:
            trending_text = trending_match.group(1)
            tags = re.findall(r'tag:\s*"([^"]+)"', trending_text)
            descs = re.findall(r'desc:\s*"([^"]+)"', trending_text)
            region_data['trending'] = list(zip(tags, descs))[:5]
        
        # 提取Opportunities
        opp_match = re.search(r'opportunities:\s*\[(.*?)\]', data_block, re.DOTALL)
        if opp_match:
            opp_text = opp_match.group(1)
            opp_tags = re.findall(r'tag:\s*"([^"]+)"', opp_text)
            opp_descs = re.findall(r'desc:\s*"([^"]+)"', opp_text)
            region_data['opportunities'] = list(zip(opp_tags, opp_descs))[:3]
        
        # 提取Competitors - 使用balanced brace匹配
        # 先找到competitors数组
        comp_arr_start = data_block.find('competitors: [')
        comp_block = data_block
        if comp_arr_start >= 0:
            cbd = 1; cbp = comp_arr_start + len('competitors: [')
            while cbd > 0 and cbp < len(data_block):
                if data_block[cbp] == '[': cbd += 1
                elif data_block[cbp] == ']': cbd -= 1
                if cbd > 0: cbp += 1
            comp_block = data_block[comp_arr_start:cbp+1]
        
        comp_names = re.findall(r'id:\s*"([^"]+)"\s*,\s*name:\s*"([^"]+)"', comp_block)
        region_data['competitors'] = []
        for comp_id, comp_name in comp_names:
            idx = comp_block.find(f'id: "{comp_id}"')
            # Search backwards from id for the opening { of the competitor object
            obj_start = comp_block.rfind('{', max(0, idx - 200), idx)
            if obj_start < 0:
                obj_start = comp_block.find('{', idx)
                if obj_start < 0: continue
            
            # Extract balanced brace block
            bd = 1; bp = obj_start + 1
            while bd > 0 and bp < len(comp_block):
                if comp_block[bp] == '{': bd += 1
                elif comp_block[bp] == '}': bd -= 1
                if bd > 0: bp += 1
            comp_obj = comp_block[obj_start:bp+1]
            
            # Find weekly block
            wk_start = comp_obj.find('weekly:')
            if wk_start < 0: continue
            wk_brace = comp_obj.find('{', wk_start)
            if wk_brace < 0: continue
            
            bd = 1; bp = wk_brace + 1
            while bd > 0 and bp < len(comp_obj):
                if comp_obj[bp] == '{': bd += 1
                elif comp_obj[bp] == '}': bd -= 1
                if bd > 0: bp += 1
            wk_block = comp_obj[wk_brace:bp+1]
            
            main_topic = re.search(r'mainTopic:\s*"([^"]+)"', wk_block)
            sentiment_p = re.search(r'positive:\s*(\d+)', wk_block)
            sentiment_n = re.search(r'negative:\s*(\d+)', wk_block)
            summary = re.search(r'summary:\s*"([^"]+)"', wk_block)
            likes = re.search(r'likes:\s*([\d.]+)', wk_block)
            comments = re.search(r'comments:\s*([\d.]+)', wk_block)
            
            region_data['competitors'].append({
                'name': comp_name,
                'topic': main_topic.group(1)[:60] if main_topic else '',
                'summary': summary.group(1)[:120] if summary else '',
                'likes': likes.group(1) if likes else '0',
                'comments': comments.group(1) if comments else '0',
                'positive': sentiment_p.group(1) if sentiment_p else '0',
                'negative': sentiment_n.group(1) if sentiment_n else '0',
            })
        
        # 提取Calendar events for today
        today_num = today.year * 10000 + today.month * 100 + today.day
        events = re.findall(
            r'date:\s*' + str(today_num) + r',\s*name:\s*"([^"]+)"[^}]*note:\s*"([^"]*)"',
            data_block
        )
        region_data['today_events'] = [(e[0], e[1][:60]) for e in events]
        
        regions_data[region_info['key']] = region_data
    
    result = {
        'update_time': update_time,
        'date_str': f"{today.strftime('%Y/%m/%d')} ({week_cn})",
        'regions': regions_data,
    }
    
    return result, None


def format_card(data):
    """生成飞书消息卡片"""
    regions = data['regions']
    
    # ===== Hot Topics Section =====
    hot_lines = []
    for rk, rd in regions.items():
        info = rd['info']
        flag = info['flag']
        top5 = rd.get('top5', [])
        if top5:
            hot_lines.append(f"**{flag} {info['name']}**")
            for item in top5[:3]:
                if item['game']:
                    hot_lines.append(f"  [{item['game']}] {item['content'][:40]}… {item['engagement']}")
            hot_lines.append("")
    
    hot_text = "\n".join(hot_lines) if hot_lines else "暂无热点数据"
    
    # ===== Trending Topics Section =====
    trending_lines = []
    all_trending = []
    for rk, rd in regions.items():
        for tag, desc in rd.get('trending', []):
            all_trending.append((tag, desc, rd['info']['flag']))
    
    # Take top trending across all regions
    seen_tags = set()
    unique_trending = []
    for tag, desc, flag in all_trending:
        if tag not in seen_tags:
            seen_tags.add(tag)
            unique_trending.append((tag, desc, flag))
    
    if unique_trending:
        for tag, desc, flag in unique_trending[:8]:
            trending_lines.append(f"  {flag} {tag} — {desc[:30]}…")
    
    trending_text = "\n".join(trending_lines) if trending_lines else "暂无热门话题数据"
    
    # ===== Today's Events Section =====
    event_lines = []
    all_events = []
    for rk, rd in regions.items():
        for name, note in rd.get('today_events', []):
            all_events.append((name, note, rd['info']['flag']))
    
    if all_events:
        for name, note, flag in all_events:
            event_lines.append(f"  {flag} {name} — {note[:40]}")
    else:
        event_lines.append("  今天无特殊营销节点")
    
    events_text = "\n".join(event_lines)
    
    # ===== Competitor Highlights Section =====
    comp_lines = []
    for rk, rd in regions.items():
        info = rd['info']
        comps = rd.get('competitors', [])
        if comps:
            # Pick the most active competitor (highest likes)
            sorted_comps = sorted(comps, key=lambda x: float(x.get('likes', '0') or '0'), reverse=True)
            top_comp = sorted_comps[0]
            comp_lines.append(f"  {info['flag']} **{top_comp['name']}**")
            comp_lines.append(f"    {top_comp['topic'][:50]}")
            comp_lines.append(f"    👍{top_comp.get('likes', '?')} 赞同 | 💬{top_comp.get('comments', '?')} 评论 | 正面{top_comp.get('positive', '?')}%")
            comp_lines.append("")
    
    comp_text = "\n".join(comp_lines) if comp_lines else "暂无竞品数据"
    
    # ===== Build Card =====
    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": f"📊 竞品分析日报 · {data['date_str']}"},
            "template": "blue"
        },
        "elements": [
            {"tag": "markdown", "content": f"**⏱ 数据更新：** {data['update_time']}"},
            {"tag": "hr"},
            {"tag": "markdown", "content": f"**🔥 今日竞品热门内容 TOP3**\n{hot_text}"},
            {"tag": "hr"},
            {"tag": "markdown", "content": f"**💬 热门话题**\n{trending_text}"},
            {"tag": "hr"},
            {"tag": "markdown", "content": f"**📅 今日营销节点**\n{events_text}"},
            {"tag": "hr"},
            {"tag": "markdown", "content": f"**🏆 竞品本周最活跃**\n{comp_text}"},
            {"tag": "hr"},
            {
                "tag": "note",
                "elements": [
                    {"tag": "plain_text", "content": "💡 数据来源：竞品SNS全量爬取 | 每日更新"},
                    {"tag": "plain_text", "content": f"  |  更新时间：{data['update_time']}"}
                ]
            }
        ]
    }
    
    return json.dumps({
        "msg_type": "interactive",
        "card": card
    }, ensure_ascii=False)


def send_card(payload_json):
    """发送到飞书Webhook"""
    if not WEBHOOK_URL:
        return False, "❌ 请先配置 FEISHU_WEBHOOK_URL"
    
    try:
        resp = requests.post(
            WEBHOOK_URL,
            data=payload_json.encode('utf-8'),
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        result = resp.json()
        if result.get("code") == 0:
            return True, "✅ 发送成功"
        else:
            return False, f"❌ 发送失败: {result}"
    except Exception as e:
        return False, f"❌ 请求异常: {e}"


def main():
    print(f"📊 竞品分析日报 · 飞书推送")
    print(f"   报告: {REPORT_PATH}")
    print(f"   日期: {datetime.now().strftime('%Y/%m/%d %H:%M')}\n")
    
    # 提取数据
    print("🔍 提取报告数据...")
    data, error = extract_all_data(REPORT_PATH)
    if error:
        print(error)
        sys.exit(1)
    
    print(f"   日期: {data['date_str']}")
    print(f"   更新时间: {data['update_time']}")
    for rk, rd in data['regions'].items():
        top_count = len(rd.get('top5', []))
        comp_count = len(rd.get('competitors', []))
        event_count = len(rd.get('today_events', []))
        print(f"   {rd['info']['flag']} {rd['info']['name']}: {top_count}热点 {comp_count}竞品 {event_count}个今日事件")
    print()
    
    # 生成卡片
    print("📝 生成消息卡片...")
    payload = format_card(data)
    print(f"   卡片大小: {len(payload)} bytes\n")
    
    # 发送
    print("📤 发送到飞书...")
    success, msg = send_card(payload)
    print(f"   {msg}")
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
