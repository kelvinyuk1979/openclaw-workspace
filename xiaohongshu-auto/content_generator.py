#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书内容生成器
生成文案草稿，保存到 posts/ 目录
"""

import json
import os
from datetime import datetime, timedelta
import random

# 配置
CONFIG_FILE = "config.json"
OUTPUT_DIR = "posts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 内容模板库
TEMPLATES = {
    "干货": [
        {
            "title": "{num}个{topic}技巧，亲测有效！",
            "content": """今天分享{num}个{topic}的实用技巧：

1️⃣ {point1}
   - {detail1}

2️⃣ {point2}
   - {detail2}

3️⃣ {point3}
   - {detail3}

这些都是我实战总结的经验，希望能帮到大家～

有疑问评论区见👇""",
        }
    ],
    "日常": [
        {
            "title": "{topic}的一天｜真实记录",
            "content": """早上{morning}
中午{noon}
晚上{evening}

今天最大的收获是{gain}

记录一下，继续加油💪

#日常 #生活记录""",
        }
    ],
    "观点": [
        {
            "title": "关于{topic}，我想说几句真心话",
            "content": """最近看到很多人讨论{topic}，说点自己的看法：

📌 观点 1: {opinion1}
📌 观点 2: {opinion2}
📌 观点 3: {opinion3}

不喜勿喷，理性讨论～

你怎么看？评论区聊聊""",
        }
    ],
}

# 量化投资主题内容库
STOCK_CONTENT = [
    {
        "topic": "短线选股",
        "num": "3",
        "point1": "看成交量",
        "detail1": "放量上涨才是真强势",
        "point2": "看均线",
        "detail2": "5 日线是短线生命线",
        "point3": "看板块",
        "detail3": "跟着热点走，别逆势操作",
    },
    {
        "topic": "止损止盈",
        "num": "2",
        "point1": "止损要坚决",
        "detail1": "到了止损位别犹豫，保住本金最重要",
        "point2": "止盈要分批",
        "detail2": "别想一口吃成胖子，分批落袋为安",
    },
    {
        "topic": "仓位管理",
        "num": "3",
        "point1": "别满仓",
        "detail1": "永远留 30% 现金应对突发",
        "point2": "分散投资",
        "detail2": "单只股票不超过总资金 20%",
        "point3": "金字塔加仓",
        "detail3": "盈利了再加仓，别越跌越买",
    },
    {
        "topic": "看盘技巧",
        "num": "4",
        "point1": "早盘 30 分钟",
        "detail1": "观察开盘后资金流向",
        "point2": "午盘休整",
        "detail2": "11:30-13:00 通常波动小",
        "point3": "尾盘异动",
        "detail3": "14:30 后注意主力动作",
        "point4": "量能配合",
        "detail4": "上涨必须放量才可靠",
    },
]

def load_config():
    """加载配置"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {
            "tags": ["#量化投资", "#股票", "#理财"],
            "niche": "量化投资/股票分析"
        }

def generate_post(template_data, content_data):
    """生成单篇笔记"""
    title = template_data["title"].format(
        num=content_data.get("num", "3"),
        topic=content_data.get("topic", "投资")
    )
    
    content = template_data["content"].format(
        num=content_data.get("num", "3"),
        topic=content_data.get("topic", "投资"),
        point1=content_data.get("point1", ""),
        detail1=content_data.get("detail1", ""),
        point2=content_data.get("point2", ""),
        detail2=content_data.get("detail2", ""),
        point3=content_data.get("point3", ""),
        detail3=content_data.get("detail3", ""),
        point4=content_data.get("point4", ""),
        detail4=content_data.get("detail4", ""),
        morning="9:00 到公司，先看隔夜美股和 A50",
        noon="午休时间复盘上午走势，调整下午策略",
        evening="收盘后写总结，准备明天的计划",
        gain="今天又避开了一个坑，纪律真的很重要",
        opinion1="市场永远是对的，别跟趋势作对",
        opinion2="亏钱不可怕，可怕的是不知道为什么亏",
        opinion3="投资是认知的变现，先提升自己再谈赚钱"
    )
    
    config = load_config()
    tags = " ".join(config.get("tags", ["#投资", "#理财"]))
    
    return f"""# {title}

{content}

---
{tags}

---
📅 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}
💡 提示：请根据实际情况调整内容后发布
"""

def save_post(content, date=None):
    """保存笔记到文件"""
    if date is None:
        date = datetime.now()
    
    filename = f"{date.strftime('%Y-%m-%d')}-{random.randint(100, 999)}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filepath

def generate_today_posts(num_posts=1):
    """生成今日笔记"""
    config = load_config()
    posts = []
    
    for i in range(num_posts):
        # 随机选择模板类型
        template_type = random.choice(list(TEMPLATES.keys()))
        template = random.choice(TEMPLATES[template_type])
        
        # 选择内容数据
        content_data = random.choice(STOCK_CONTENT)
        
        # 生成内容
        post_content = generate_post(template, content_data)
        
        # 保存
        filepath = save_post(post_content)
        posts.append(filepath)
        
        print(f"✅ 生成笔记：{filepath}")
    
    return posts

if __name__ == "__main__":
    print("=" * 60)
    print("📝 小红书内容生成器")
    print("=" * 60)
    print()
    
    posts = generate_today_posts(1)
    
    print()
    print("=" * 60)
    print(f"✅ 完成！生成了 {len(posts)} 篇笔记")
    print(f"📁 保存位置：{os.path.abspath(OUTPUT_DIR)}")
    print()
    print("下一步:")
    print("  1. 打开生成的 .md 文件查看内容")
    print("  2. 根据需要调整文案")
    print("  3. 手动发布到小红书 (推荐)")
    print("=" * 60)
