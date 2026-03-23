#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小众股票自动跟踪脚本
每日获取价格、涨跌幅、成交量等数据，生成观察报告
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# 输出目录
OUTPUT_DIR = Path("/Users/kelvin/.openclaw/workspace/projects/stock-tracking")
OUTPUT_DIR.mkdir(exist_ok=True)

# 股票池配置
NICHE_STOCKS = {
    "A 股隐形冠军": [
        {"code": "688111", "name": "金山办公", "sector": "软件"},
        {"code": "688012", "name": "中微公司", "sector": "半导体"},
        {"code": "300763", "name": "锦浪科技", "sector": "光伏"},
        {"code": "688390", "name": "固德威", "sector": "光伏"},
        {"code": "300861", "name": "美畅股份", "sector": "光伏"},
        {"code": "688122", "name": "西部超导", "sector": "材料"},
        {"code": "300601", "name": "康泰生物", "sector": "医药"},
        {"code": "688016", "name": "心脉医疗", "sector": "医药"},
        {"code": "300723", "name": "一品红", "sector": "医药"},
        {"code": "688180", "name": "君实生物", "sector": "医药"},
    ],
    "北交所专精特新": [
        {"code": "833575", "name": "康乐卫士", "sector": "医药"},
        {"code": "835185", "name": "贝特瑞", "sector": "新能源"},
        {"code": "830779", "name": "武汉蓝电", "sector": "设备"},
        {"code": "832000", "name": "寰宇科技", "sector": "军工"},
        {"code": "872925", "name": "锦好医疗", "sector": "医药"},
    ],
    "港股隐形冠军": [
        {"code": "02269.HK", "name": "药明生物", "sector": "医药"},
        {"code": "01801.HK", "name": "信达生物", "sector": "医药"},
        {"code": "09995.HK", "name": "再鼎医药", "sector": "医药"},
        {"code": "02208.HK", "name": "金风科技", "sector": "新能源"},
        {"code": "01799.HK", "name": "协鑫新能源", "sector": "光伏"},
    ]
}

def get_stock_data_fallback():
    """
    获取股票数据（模拟版本）
    实际使用时应接入真实数据源（如 akshare、tushare、Yahoo Finance 等）
    """
    import random
    
    data = {}
    for category, stocks in NICHE_STOCKS.items():
        for stock in stocks:
            # 模拟价格数据（实际应调用 API）
            base_price = random.uniform(10, 500)
            change_pct = random.uniform(-5, 5)
            volume = random.randint(100000, 10000000)
            
            key = f"{stock['code']}_{stock['name']}"
            data[key] = {
                "code": stock["code"],
                "name": stock["name"],
                "category": category,
                "sector": stock["sector"],
                "price": round(base_price, 2),
                "change_pct": round(change_pct, 2),
                "volume": volume,
                "market_cap": round(base_price * random.uniform(1, 10), 2),
                "timestamp": datetime.now().isoformat()
            }
    
    return data

def analyze_stock(data):
    """分析股票数据，生成买卖信号"""
    signals = {}
    
    for key, stock in data.items():
        signal = {
            "code": stock["code"],
            "name": stock["name"],
            "action": "持有",
            "reason": "",
            "confidence": 50
        }
        
        # 简单策略：涨跌幅判断
        if stock["change_pct"] > 3:
            signal["action"] = "关注"
            signal["reason"] = "强势上涨"
            signal["confidence"] = 70
        elif stock["change_pct"] < -3:
            signal["action"] = "警惕"
            signal["reason"] = "大幅回调"
            signal["confidence"] = 70
        elif stock["change_pct"] > 5:
            signal["action"] = "追涨"
            signal["reason"] = "突破行情"
            signal["confidence"] = 80
        elif stock["change_pct"] < -5:
            signal["action"] = "抄底机会"
            signal["reason"] = "超跌反弹"
            signal["confidence"] = 60
        
        signals[key] = signal
    
    return signals

def generate_daily_report(data, signals):
    """生成每日跟踪报告"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    report = f"""# 🔍 小众股票每日跟踪报告
**日期：** {date_str}
**覆盖股票：** {len(data)} 只
**更新时间：** {datetime.now().strftime("%H:%M")}

---

## 📊 市场概览

| 分类 | 股票数 | 上涨 | 下跌 | 平均涨幅 |
|------|--------|------|------|----------|
"""
    
    # 按分类统计
    for category in NICHE_STOCKS.keys():
        category_stocks = [s for k, s in data.items() if s["category"] == category]
        up_count = sum(1 for s in category_stocks if s["change_pct"] > 0)
        down_count = sum(1 for s in category_stocks if s["change_pct"] < 0)
        avg_change = sum(s["change_pct"] for s in category_stocks) / len(category_stocks)
        
        report += f"| {category} | {len(category_stocks)} | {up_count} | {down_count} | {avg_change:+.2f}% |\n"
    
    report += """
---

## 🚨 今日信号

"""
    
    # 列出所有信号
    buy_signals = [(k, v) for k, v in signals.items() if v["action"] in ["追涨", "抄底机会", "关注"]]
    sell_signals = [(k, v) for k, v in signals.items() if v["action"] in ["警惕"]]
    
    if buy_signals:
        report += "### 🟢 买入/关注信号\n\n"
        report += "| 代码 | 名称 | 信号 | 原因 | 置信度 |\n"
        report += "|------|------|------|------|--------|\n"
        for key, signal in buy_signals:
            report += f"| {signal['code']} | {signal['name']} | {signal['action']} | {signal['reason']} | {signal['confidence']}% |\n"
        report += "\n"
    
    if sell_signals:
        report += "### 🔴 卖出/警惕信号\n\n"
        report += "| 代码 | 名称 | 信号 | 原因 | 置信度 |\n"
        report += "|------|------|------|------|--------|\n"
        for key, signal in sell_signals:
            report += f"| {signal['code']} | {signal['name']} | {signal['action']} | {signal['reason']} | {signal['confidence']}% |\n"
        report += "\n"
    
    report += """---

## 📈 个股详情

"""
    
    # 按分类列出个股
    for category in NICHE_STOCKS.keys():
        report += f"### {category}\n\n"
        report += "| 代码 | 名称 | 现价 | 涨跌幅 | 成交量 | 信号 |\n"
        report += "|------|------|------|--------|--------|------|\n"
        
        for key, stock in data.items():
            if stock["category"] == category:
                signal = signals[key]["action"]
                signal_emoji = {"追涨": "🟢", "关注": "🟡", "持有": "⚪", "警惕": "🔴", "抄底机会": "💎"}.get(signal, "⚪")
                report += f"| {stock['code']} | {stock['name']} | {stock['price']} | {stock['change_pct']:+.2f}% | {stock['volume']:,} | {signal_emoji} {signal} |\n"
        
        report += "\n"
    
    report += f"""---

## 💡 操作建议

1. **今日重点关注：** 涨幅前 3 的股票
2. **风险警示：** 跌幅超过 5% 的股票需警惕
3. **仓位控制：** 单只股票不超过 10%
4. **止损纪律：** 严格执行 -15% 止损线

---

*报告生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*数据来源：模拟数据（实际使用需接入真实 API）*
*免责声明：仅供参考，不构成投资建议*
"""
    
    return report

def send_email_report(report_content, subject):
    """发送邮件报告"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    EMAIL_CONFIG = {
        "smtp_server": "smtp.qq.com",
        "smtp_port": 465,
        "from_email": "4352395@qq.com",
        "password": "eryjlcbeanxnbgcj",
        "to_email": "4352395@qq.com"
    }
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_CONFIG["from_email"]
    msg["To"] = EMAIL_CONFIG["to_email"]
    
    # 转换为 HTML
    html_content = report_content.replace("# ", "<h1>").replace("## ", "<h2>").replace("### ", "<h3>")
    html_content = html_content.replace("\n", "<br>")
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 900px; margin: 0 auto; padding: 20px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background: #667eea; color: white; }}
            .green {{ color: #27ae60; }}
            .red {{ color: #c0392b; }}
            h1 {{ color: #667eea; }}
            h2 {{ color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    html_part = MIMEText(html_content, "html", "utf-8")
    msg.attach(html_part)
    
    try:
        server = smtplib.SMTP_SSL(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"])
        server.login(EMAIL_CONFIG["from_email"], EMAIL_CONFIG["password"])
        server.sendmail(EMAIL_CONFIG["from_email"], [EMAIL_CONFIG["to_email"]], msg.as_string())
        server.quit()
        print("✅ 邮件发送成功！")
        return True
    except Exception as e:
        print(f"❌ 邮件发送失败：{e}")
        return False

def main():
    """主函数"""
    print("🔍 开始获取小众股票数据...")
    
    # 获取数据
    data = get_stock_data_fallback()
    print(f"✅ 获取到 {len(data)} 只股票数据")
    
    # 分析信号
    print("📊 分析股票信号...")
    signals = analyze_stock(data)
    
    # 生成报告
    print("📝 生成每日跟踪报告...")
    report = generate_daily_report(data, signals)
    
    # 保存到文件
    date_str = datetime.now().strftime("%Y-%m-%d")
    report_file = OUTPUT_DIR / f"niche-stocks-daily-{date_str}.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"✅ 报告已保存：{report_file}")
    
    # 发送邮件
    print("📧 发送邮件报告...")
    subject = f"🔍 小众股票每日跟踪 - {date_str}"
    send_email_report(report, subject)
    
    # 保存数据到 JSON（用于后续分析）
    data_file = OUTPUT_DIR / f"niche-stocks-data-{date_str}.json"
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 数据已保存：{data_file}")
    
    print("\n✅ 小众股票跟踪完成！")

if __name__ == "__main__":
    main()
