#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polymarket 天气交易机器人 - 每日邮件报告
发送模拟交易日报到用户邮箱
"""

import smtplib
import json
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

# 加载配置
def load_config():
    """加载邮箱配置"""
    config_paths = [
        Path(__file__).parent / 'email_config.json',
        Path(__file__).parent / 'config.json',
    ]
    
    for path in config_paths:
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    # 默认配置（需要用户填写）
    return {
        "email": {
            "smtp_server": "smtp.qq.com",
            "smtp_port": 587,
            "from_email": "your_qq@qq.com",
            "password": "your_smtp_password",
            "to_email": "4352395@qq.com"
        }
    }


def generate_daily_report(sim_data: dict, signals: list, trades_today: int) -> str:
    """
    生成每日报告（HTML 格式）
    
    Args:
        sim_data: 模拟账户数据
        signals: 今日信号列表
        trades_today: 今日交易数
    """
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 计算统计
    balance = sim_data.get('balance', 1000.0)
    starting = sim_data.get('starting_balance', 1000.0)
    profit = balance - starting
    profit_pct = (profit / starting) * 100 if starting > 0 else 0
    total_trades = sim_data.get('total_trades', 0)
    wins = sim_data.get('wins', 0)
    losses = sim_data.get('losses', 0)
    win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
    
    # 最低价格信号
    top_signals = sorted(signals, key=lambda x: x.get('price', 1.0))[:5]
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .header p {{ margin: 10px 0 0; opacity: 0.9; }}
        .section {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 15px; }}
        .section h2 {{ color: #667eea; margin-top: 0; font-size: 18px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .metric-value {{ font-size: 28px; font-weight: bold; color: #667eea; }}
        .metric-label {{ font-size: 14px; color: #666; }}
        .positive {{ color: #28a745; }}
        .negative {{ color: #dc3545; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #667eea; color: white; }}
        tr:hover {{ background: #f5f5f5; }}
        .badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
        .badge-success {{ background: #28a745; color: white; }}
        .badge-warning {{ background: #ffc107; color: #333; }}
        .badge-info {{ background: #17a2b8; color: white; }}
        .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌤️ Polymarket 天气交易机器人 - 每日报告</h1>
            <p>报告日期：{today}</p>
        </div>
        
        <div class="section">
            <h2>💰 账户概览</h2>
            <div class="metric">
                <div class="metric-value">${balance:.2f}</div>
                <div class="metric-label">当前余额</div>
            </div>
            <div class="metric">
                <div class="metric-value">${profit:+.2f}</div>
                <div class="metric-label">总盈亏</div>
            </div>
            <div class="metric">
                <div class="metric-value { 'positive' if profit >= 0 else 'negative' }">{profit_pct:+.2f}%</div>
                <div class="metric-label">收益率</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 交易统计</h2>
            <table>
                <tr>
                    <th>指标</th>
                    <th>数值</th>
                </tr>
                <tr>
                    <td>总交易数</td>
                    <td>{total_trades}</td>
                </tr>
                <tr>
                    <td>获胜</td>
                    <td>{wins}</td>
                </tr>
                <tr>
                    <td>失败</td>
                    <td>{losses}</td>
                </tr>
                <tr>
                    <td>胜率</td>
                    <td>{win_rate:.1f}%</td>
                </tr>
                <tr>
                    <td>今日信号</td>
                    <td>{len(signals)}</td>
                </tr>
                <tr>
                    <td>今日交易</td>
                    <td>{trades_today}</td>
                </tr>
            </table>
        </div>
        
        <div class="section">
            <h2>🎯 最低价格信号 Top 5</h2>
            <table>
                <tr>
                    <th>城市</th>
                    <th>日期</th>
                    <th>预报温度</th>
                    <th>市场价格</th>
                    <th>建议</th>
                </tr>
"""
    
    for i, sig in enumerate(top_signals, 1):
        price = sig.get('price', 0)
        if price < 0.22:
            badge = '<span class="badge badge-success">建议入场</span>'
        elif price < 0.30:
            badge = '<span class="badge badge-warning">关注</span>'
        else:
            badge = '<span class="badge badge-info">观察</span>'
        
        html += f"""
                <tr>
                    <td>{sig.get('city', 'N/A')}</td>
                    <td>{sig.get('date', 'N/A')}</td>
                    <td>{sig.get('forecast_temp', 'N/A')}°F</td>
                    <td>${price:.3f}</td>
                    <td>{badge}</td>
                </tr>
"""
    
    html += f"""
            </table>
        </div>
        
        <div class="section">
            <h2>📈 策略参数</h2>
            <table>
                <tr>
                    <th>参数</th>
                    <th>当前值</th>
                </tr>
                <tr>
                    <td>入场阈值</td>
                    <td>22¢ (市场价格 &lt; 0.22)</td>
                </tr>
                <tr>
                    <td>出场阈值</td>
                    <td>50¢ (价格 ≥ 0.50 卖出)</td>
                </tr>
                <tr>
                    <td>单笔仓位</td>
                    <td>余额的 3%</td>
                </tr>
                <tr>
                    <td>最大交易数</td>
                    <td>5 笔/次</td>
                </tr>
            </table>
        </div>
        
        <div class="section">
            <h2>📝 今日总结</h2>
            <ul>
                <li>今日发现 <strong>{len(signals)}</strong> 个匹配信号</li>
                <li>其中 <strong>{sum(1 for s in signals if s.get('price', 1) < 0.22)}</strong> 个低于入场阈值</li>
                <li>执行模拟交易 <strong>{trades_today}</strong> 笔</li>
                <li>当前持仓 <strong>{len(sim_data.get('pending_positions', {}))}</strong> 个</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>Polymarket 天气交易机器人 v1.0 | 模拟交易 | 不构成投资建议</p>
            <p>数据源：NWS (美国国家气象局) | Polymarket Gamma API</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html


def send_email(subject: str, html_content: str, to_email: str):
    """发送邮件"""
    config = load_config()
    email_config = config.get('email', {})
    
    smtp_server = email_config.get('smtp_server', 'smtp.qq.com')
    smtp_port = email_config.get('smtp_port', 587)
    from_email = email_config.get('from_email', '')
    password = email_config.get('password', '')
    to_email = email_config.get('to_email', to_email)
    
    if not password or from_email == 'your_qq@qq.com':
        print(f"⚠️  邮箱配置未设置，邮件内容已保存到 email_draft.html")
        with open('email_draft.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        return False
    
    try:
        # 创建邮件
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        
        # 添加 HTML 内容
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # 发送
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, [to_email], msg.as_string())
        server.quit()
        
        print(f"✅ 邮件已发送：{to_email}")
        return True
        
    except Exception as e:
        print(f"❌ 邮件发送失败：{e}")
        # 保存草稿
        with open('email_draft.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"📄 邮件内容已保存到 email_draft.html")
        return False


def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description='发送每日邮件报告')
    parser.add_argument('--to', type=str, help='收件人邮箱')
    args = parser.parse_args()
    
    config = load_config()
    to_email = args.to or config.get('email', {}).get('to_email', '4352395@qq.com')
    
    # 加载模拟数据
    sim_file = Path(__file__).parent / 'simulation.json'
    if sim_file.exists():
        with open(sim_file, 'r', encoding='utf-8') as f:
            sim_data = json.load(f)
    else:
        sim_data = {"balance": 1000.0, "starting_balance": 1000.0}
    
    # 加载今日信号（从日志或单独的文件）
    signals_file = Path(__file__).parent / 'today_signals.json'
    if signals_file.exists():
        with open(signals_file, 'r', encoding='utf-8') as f:
            signals = json.load(f)
    else:
        signals = []
    
    # 生成报告
    trades_today = sim_data.get('total_trades', 0)
    html_content = generate_daily_report(sim_data, signals, trades_today)
    
    # 发送邮件
    subject = f"🌤️ Polymarket 天气交易日报 - {datetime.now().strftime('%Y-%m-%d')}"
    send_email(subject, html_content, to_email)


if __name__ == "__main__":
    main()
