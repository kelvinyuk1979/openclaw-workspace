#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小众股票每周复盘脚本
每周五收盘后执行，生成周度复盘报告
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# 输出目录
OUTPUT_DIR = Path("/Users/kelvin/.openclaw/workspace/projects/stock-tracking")
OUTPUT_DIR.mkdir(exist_ok=True)

def load_weekly_data():
    """加载本周数据"""
    today = datetime.now()
    # 找到本周一
    monday = today - timedelta(days=today.weekday())
    
    weekly_data = {}
    
    # 加载本周所有数据文件
    for i in range(5):  # 周一到周五
        date = monday + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        data_file = OUTPUT_DIR / f"niche-stocks-data-{date_str}.json"
        
        if data_file.exists():
            with open(data_file, "r", encoding="utf-8") as f:
                daily_data = json.load(f)
                weekly_data[date_str] = daily_data
    
    return weekly_data

def analyze_weekly_performance(weekly_data):
    """分析本周表现"""
    if not weekly_data:
        return None
    
    # 获取最早和最新数据
    dates = sorted(weekly_data.keys())
    first_date = dates[0]
    last_date = dates[-1]
    
    first_data = weekly_data[first_date]
    last_data = weekly_data[last_date]
    
    analysis = {
        "period": f"{first_date} ~ {last_date}",
        "trading_days": len(dates),
        "stocks": {}
    }
    
    # 计算每只股票的周涨跌幅
    for key, last_stock in last_data.items():
        if key in first_data:
            first_stock = first_data[key]
            weekly_change = ((last_stock["price"] - first_stock["price"]) / first_stock["price"] * 100)
            
            analysis["stocks"][key] = {
                "code": last_stock["code"],
                "name": last_stock["name"],
                "category": last_stock["category"],
                "start_price": first_stock["price"],
                "end_price": last_stock["price"],
                "weekly_change": round(weekly_change, 2),
                "avg_volume": sum(weekly_data[d][key]["volume"] for d in dates if key in weekly_data[d]) // len([d for d in dates if key in weekly_data[d]])
            }
    
    return analysis

def generate_weekly_report(analysis):
    """生成周度复盘报告"""
    week_num = datetime.now().isocalendar()[1]
    year = datetime.now().year
    
    report = f"""# 📊 小众股票每周复盘报告
**期数：** 第{week_num}周 ({year}年)
**周期：** {analysis["period"]}
**交易日：** {analysis["trading_days"]} 天

---

## 📈 本周表现概览

### 整体统计
| 指标 | 数值 |
|------|------|
| 跟踪股票数 | {len(analysis["stocks"])} 只 |
| 上涨股票 | {sum(1 for s in analysis["stocks"].values() if s["weekly_change"] > 0)} 只 |
| 下跌股票 | {sum(1 for s in analysis["stocks"].values() if s["weekly_change"] < 0)} 只 |
| 持平股票 | {sum(1 for s in analysis["stocks"].values() if s["weekly_change"] == 0)} 只 |

### 分类表现
| 分类 | 股票数 | 平均周涨幅 | 最佳股票 | 最差股票 |
|------|--------|------------|----------|----------|
"""
    
    # 按分类统计
    categories = {}
    for stock in analysis["stocks"].values():
        cat = stock["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(stock)
    
    for cat, stocks in categories.items():
        avg_change = sum(s["weekly_change"] for s in stocks) / len(stocks)
        best = max(stocks, key=lambda x: x["weekly_change"])
        worst = min(stocks, key=lambda x: x["weekly_change"])
        
        report += f"| {cat} | {len(stocks)} | {avg_change:+.2f}% | {best['name']} ({best['weekly_change']:+.1f}%) | {worst['name']} ({worst['weekly_change']:+.1f}%) |\n"
    
    report += """
---

## 🏆 本周最佳表现

### 🥇 涨幅前三

| 排名 | 代码 | 名称 | 分类 | 周涨幅 | 周末收盘价 |
|------|------|------|------|--------|------------|
"""
    
    top3 = sorted(analysis["stocks"].values(), key=lambda x: x["weekly_change"], reverse=True)[:3]
    for i, stock in enumerate(top3, 1):
        medal = ["🥇", "🥈", "🥉"][i-1]
        report += f"| {medal} | {stock['code']} | {stock['name']} | {stock['category']} | {stock['weekly_change']:+.2f}% | {stock['end_price']} |\n"
    
    report += """
### 📉 跌幅前三

| 排名 | 代码 | 名称 | 分类 | 周跌幅 | 周末收盘价 |
|------|------|------|------|--------|------------|
"""
    
    bottom3 = sorted(analysis["stocks"].values(), key=lambda x: x["weekly_change"])[:3]
    for i, stock in enumerate(bottom3, 1):
        report += f"| {i} | {stock['code']} | {stock['name']} | {stock['category']} | {stock['weekly_change']:+.2f}% | {stock['end_price']} |\n"
    
    report += """
---

## 📋 分类复盘

"""
    
    for cat, stocks in categories.items():
        report += f"### {cat}\n\n"
        report += "| 代码 | 名称 | 周涨幅 | 成交量 | 点评 |\n"
        report += "|------|------|--------|--------|------|\n"
        
        for stock in sorted(stocks, key=lambda x: x["weekly_change"], reverse=True):
            comment = "强势" if stock["weekly_change"] > 5 else "稳健" if stock["weekly_change"] > 0 else "调整" if stock["weekly_change"] > -5 else "弱势"
            report += f"| {stock['code']} | {stock['name']} | {stock['weekly_change']:+.2f}% | {stock['avg_volume']:,} | {comment} |\n"
        
        report += "\n"
    
    report += """---

## 💡 操作建议

### 下周重点关注
1. **继续持有：** 本周涨幅前 3 的股票（趋势延续）
2. **逢低吸纳：** 本周下跌但基本面良好的股票
3. **警惕风险：** 本周跌幅超过 10% 的股票（可能有基本面问题）

### 仓位调整建议
| 股票 | 当前仓位 | 建议操作 | 理由 |
|------|----------|----------|------|
| [待分析] | -- | 持有/加仓/减仓 | -- |

### 止损检查
- [ ] 检查是否有股票触发 -15% 止损线
- [ ] 检查是否有股票接近止损线（-10% 至 -15%）
- [ ] 评估是否需要提前止损

---

## 📅 下周计划

### 建仓计划
- [ ] 第一批建仓股票：[待填]
- [ ] 建仓价格区间：[待填]
- [ ] 目标仓位：[待填]

### 关注事件
- [ ] 财报发布：[待填]
- [ ] 行业政策：[待填]
- [ ] 重要会议：[待填]

---

## 📝 本周重要事件

### 公司公告
[待补充]

### 行业新闻
[待补充]

### 政策变化
[待补充]

---

## 🎯 本月累计表现

| 指标 | 数值 |
|------|------|
| 本月交易周 | 第 X 周 |
| 月累计收益 | +X% |
| 最佳股票 | [待填] |
| 最差股票 | [待填] |

---

*报告生成时间：{}*
*数据来源：小众股票跟踪系统*
*免责声明：仅供参考，不构成投资建议*
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
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
    
    html_content = report_content.replace("# ", "<h1>").replace("## ", "<h2>").replace("### ", "<h3>")
    html_content = html_content.replace("\n", "<br>")
    
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
    print("📊 开始生成本周复盘报告...")
    
    # 加载本周数据
    weekly_data = load_weekly_data()
    
    if not weekly_data:
        print("⚠️  本周暂无数据，跳过复盘")
        return
    
    print(f"✅ 加载到 {len(weekly_data)} 个交易日的数据")
    
    # 分析本周表现
    print("📈 分析本周表现...")
    analysis = analyze_weekly_performance(weekly_data)
    
    if not analysis:
        print("⚠️  分析失败，跳过复盘")
        return
    
    # 生成报告
    print("📝 生成周度复盘报告...")
    report = generate_weekly_report(analysis)
    
    # 保存到文件
    week_num = datetime.now().isocalendar()[1]
    year = datetime.now().year
    report_file = OUTPUT_DIR / f"niche-stocks-weekly-{year}-W{week_num:02d}.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"✅ 报告已保存：{report_file}")
    
    # 发送邮件
    print("📧 发送邮件报告...")
    subject = f"📊 小众股票每周复盘 - {year}年第{week_num}周"
    send_email_report(report, subject)
    
    print("\n✅ 每周复盘完成！")

if __name__ == "__main__":
    main()
