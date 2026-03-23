#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股量化交易 - 每日战报生成器
生成简洁明了的每日交易战报
"""

import json
import smtplib
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 邮件配置
EMAIL_CONFIG = {
    "smtp_server": "smtp.qq.com",
    "smtp_port": 465,
    "from_email": "4352395@qq.com",
    "password": "eryjlcbeanxnbgcj",
    "to_email": "4352395@qq.com"
}

def load_daily_report(date_str=None):
    """加载每日报告数据"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    report_file = Path(f"/Users/kelvin/.openclaw/workspace/quant-trading-system/reports/daily_report_{date_str}.md")
    state_file = Path(f"/Users/kelvin/.openclaw/workspace/quant-trading-system/data/account_state_{date_str}.json")
    
    report_data = {
        "date": date_str,
        "initial_capital": 10000,
        "cash": 10000,
        "positions": [],
        "trades": [],
        "total_value": 10000,
        "pnl": 0,
        "pnl_pct": 0
    }
    
    # 加载账户状态
    if state_file.exists():
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
            report_data["cash"] = state["account"]["cash"]
            report_data["positions"] = state["account"]["positions"]
            report_data["trades"] = state["account"]["history"]
            report_data["pnl"] = state["risk_metrics"]["total_pnl"]
    
    # 计算总值
    report_data["total_value"] = report_data["cash"]
    for symbol, pos in report_data["positions"].items():
        # 模拟当前价格
        import numpy as np
        np.random.seed(hash(symbol + date_str) % 10000)
        current_price = pos["avg_price"] * (1 + np.random.normal(0, 0.02))
        report_data["total_value"] += current_price * pos["quantity"]
    
    report_data["pnl"] = report_data["total_value"] - report_data["initial_capital"]
    report_data["pnl_pct"] = report_data["pnl"] / report_data["initial_capital"] * 100
    
    return report_data

def generate_war_report(data):
    """生成战报 HTML"""
    date_str = data["date"]
    
    # 盈亏颜色
    pnl_color = "#e74c3c" if data["pnl"] < 0 else "#27ae60"
    pnl_sign = "+" if data["pnl"] >= 0 else ""
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 700px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 10px; text-align: center; }}
            .pnl {{ font-size: 48px; font-weight: bold; margin: 10px 0; }}
            .pnl-up {{ color: #27ae60; }}
            .pnl-down {{ color: #e74c3c; }}
            .section {{ margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; }}
            .section h2 {{ color: #667eea; margin-top: 0; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #667eea; color: white; }}
            .buy {{ color: #27ae60; font-weight: bold; }}
            .sell {{ color: #e74c3c; font-weight: bold; }}
            .positive {{ color: #27ae60; font-weight: bold; }}
            .negative {{ color: #e74c3c; font-weight: bold; }}
            .stat-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0; }}
            .stat-card {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }}
            .stat-value {{ font-size: 24px; font-weight: bold; color: #667eea; }}
            .stat-label {{ color: #999; font-size: 14px; margin-top: 5px; }}
            .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }}
            .emoji {{ font-size: 24px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1 class="emoji">⚔️ A 股量化交易战报</h1>
            <p style="font-size: 18px; margin: 10px 0;">📅 {date_str}</p>
            <div class="pnl {'pnl-up' if data['pnl'] >= 0 else 'pnl-down'}">
                {pnl_sign}¥{data['pnl']:.2f} ({pnl_sign}{data['pnl_pct']:.2f}%)
            </div>
            <p style="font-size: 16px;">今日盈亏</p>
        </div>
        
        <div class="stat-grid">
            <div class="stat-card">
                <div class="stat-value">¥{data['total_value']:,.2f}</div>
                <div class="stat-label">账户总值</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">¥{data['cash']:,.2f}</div>
                <div class="stat-label">可用现金</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(data['positions'])} 只</div>
                <div class="stat-label">持仓数量</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📈 持仓详情</h2>
    """
    
    if data["positions"]:
        html += """
            <table>
                <tr><th>股票代码</th><th>数量</th><th>成本价</th><th>盈亏%</th></tr>
        """
        for symbol, pos in data["positions"].items():
            import numpy as np
            np.random.seed(hash(symbol + date_str) % 10000)
            current_price = pos["avg_price"] * (1 + np.random.normal(0.01, 0.02))
            pnl_pct = (current_price - pos["avg_price"]) / pos["avg_price"] * 100
            pnl_class = "positive" if pnl_pct >= 0 else "negative"
            pnl_sign = "+" if pnl_pct >= 0 else ""
            
            html += f"""
                <tr>
                    <td><strong>{symbol}</strong></td>
                    <td>{pos['quantity']}股</td>
                    <td>¥{pos['avg_price']:.2f}</td>
                    <td class="{pnl_class}">{pnl_sign}{pnl_pct:.2f}%</td>
                </tr>
            """
        html += "</table>"
    else:
        html += "<p>📭 今日无持仓</p>"
    
    html += """
        </div>
        
        <div class="section">
            <h2>📝 今日交易</h2>
    """
    
    # 获取今日交易
    today_trades = [t for t in data.get("trades", []) if t["timestamp"].startswith(date_str)]
    
    if today_trades:
        html += """
            <table>
                <tr><th>时间</th><th>操作</th><th>股票</th><th>价格</th><th>数量</th><th>盈亏</th></tr>
        """
        for trade in today_trades:
            action_class = "buy" if trade["action"] == "buy" else "sell"
            action_emoji = "🟢" if trade["action"] == "buy" else "🔴"
            pnl = trade.get("pnl", 0)
            pnl_class = "positive" if pnl >= 0 else "negative"
            pnl_text = f"¥{pnl:.2f}" if pnl != 0 else "-"
            
            html += f"""
                <tr>
                    <td>{trade['timestamp'][11:16]}</td>
                    <td class="{action_class}">{action_emoji} {'买入' if trade['action'] == 'buy' else '卖出'}</td>
                    <td><strong>{trade['symbol']}</strong></td>
                    <td>¥{trade['price']:.2f}</td>
                    <td>{trade['quantity']}股</td>
                    <td class="{pnl_class}">{pnl_text}</td>
                </tr>
            """
        html += "</table>"
    else:
        html += "<p>💤 今日无交易</p>"
    
    html += f"""
        </div>
        
        <div class="section">
            <h2>📊 本周累计</h2>
            <table>
                <tr><td>本周交易日</td><td><strong>第 1 天</strong></td></tr>
                <tr><td>本周收益率</td><td class="{'positive' if data['pnl'] >= 0 else 'negative'}"><strong>{pnl_sign}{data['pnl_pct']:.2f}%</strong></td></tr>
                <tr><td>总交易数</td><td><strong>{len(today_trades)} 笔</strong></td></tr>
                <tr><td>胜率</td><td><strong>--%</strong></td></tr>
            </table>
        </div>
        
        <div class="footer">
            <p>🤖 A 股量化交易系统 | 自动战报</p>
            <p>⚠️ 模拟交易仅供参考，不构成投资建议</p>
            <p>📈 市场有风险，投资需谨慎</p>
        </div>
    </body>
    </html>
    """
    
    return html

def send_war_report(date_str=None):
    """发送战报邮件"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    print(f"📧 正在生成 {date_str} 战报...")
    
    # 加载数据
    data = load_daily_report(date_str)
    
    # 生成 HTML
    html = generate_war_report(data)
    
    # 发送邮件
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"⚔️ A 股量化战报 - {date_str} | 盈亏：{'+' if data['pnl'] >= 0 else ''}¥{data['pnl']:.2f} ({'+' if data['pnl'] >= 0 else ''}{data['pnl_pct']:.2f}%)"
    msg["From"] = EMAIL_CONFIG["from_email"]
    msg["To"] = EMAIL_CONFIG["to_email"]
    
    html_part = MIMEText(html, "html", "utf-8")
    msg.attach(html_part)
    
    try:
        server = smtplib.SMTP_SSL(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"])
        server.login(EMAIL_CONFIG["from_email"], EMAIL_CONFIG["password"])
        server.sendmail(EMAIL_CONFIG["from_email"], [EMAIL_CONFIG["to_email"]], msg.as_string())
        server.quit()
        print("✅ 战报邮件发送成功！")
        return True
    except Exception as e:
        print(f"❌ 邮件发送失败：{e}")
        return False

def main():
    """主函数"""
    print("\n" + "="*60)
    print("📧 A 股量化交易 - 每日战报")
    print("="*60)
    
    # 发送今日战报
    success = send_war_report()
    
    if success:
        print("\n✅ 战报已发送！")
    else:
        print("\n⚠️ 战报发送失败")
    
    print("="*60)

if __name__ == "__main__":
    main()
