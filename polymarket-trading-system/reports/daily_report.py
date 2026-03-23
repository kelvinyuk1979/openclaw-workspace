#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polymarket 统一交易系统 - 每日报告
"""

import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent


def generate_html_report(quant: dict, weather: dict, event: dict, config: dict) -> str:
    """生成统一 HTML 报告"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 汇总统计
    total_signals = (
        len(quant.get('signals', [])) + 
        len(weather.get('signals', [])) + 
        len(event.get('signals', []))
    )
    total_trades = (
        quant.get('trades', 0) + 
        weather.get('trades', 0) + 
        event.get('trades', 0)
    )
    
    # 账户概览
    initial = config['account']['initial_capital']
    balance = config['account']['initial_capital']  # 实际应从账户状态读取
    profit = balance - initial
    profit_pct = (profit / initial) * 100 if initial > 0 else 0
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .section {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 15px; }}
        .section h2 {{ color: #667eea; margin-top: 0; font-size: 18px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
        .strategy-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 15px 0; }}
        .strategy-card {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .strategy-card h3 {{ margin: 0 0 10px; font-size: 16px; color: #667eea; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #667eea; }}
        .metric-label {{ font-size: 13px; color: #666; }}
        .positive {{ color: #28a745; }}
        .negative {{ color: #dc3545; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #667eea; color: white; }}
        .badge {{ display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
        .badge-quant {{ background: #667eea; color: white; }}
        .badge-weather {{ background: #17a2b8; color: white; }}
        .badge-event {{ background: #ffc107; color: #333; }}
        .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Polymarket 统一交易系统 - 每日报告</h1>
            <p>报告日期：{today}</p>
        </div>
        
        <div class="section">
            <h2>💰 账户概览</h2>
            <div class="metric">
                <div class="metric-value">${balance:,.2f}</div>
                <div class="metric-label">当前余额</div>
            </div>
            <div class="metric">
                <div class="metric-value">${profit:+,.2f}</div>
                <div class="metric-label">总盈亏</div>
            </div>
            <div class="metric">
                <div class="metric-value {'positive' if profit >= 0 else 'negative'}">{profit_pct:+.2f}%</div>
                <div class="metric-label">收益率</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 策略表现</h2>
            <div class="strategy-grid">
                <div class="strategy-card">
                    <h3>📈 量化核心</h3>
                    <div class="metric">
                        <div class="metric-value">{len(quant.get('signals', []))}</div>
                        <div class="metric-label">信号数</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{quant.get('trades', 0)}</div>
                        <div class="metric-label">交易数</div>
                    </div>
                </div>
                <div class="strategy-card">
                    <h3>🌤️ 天气套利</h3>
                    <div class="metric">
                        <div class="metric-value">{len(weather.get('signals', []))}</div>
                        <div class="metric-label">信号数</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{weather.get('trades', 0)}</div>
                        <div class="metric-label">交易数</div>
                    </div>
                </div>
                <div class="strategy-card">
                    <h3>📅 事件交易</h3>
                    <div class="metric">
                        <div class="metric-value">{len(event.get('signals', []))}</div>
                        <div class="metric-label">信号数</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{event.get('trades', 0)}</div>
                        <div class="metric-label">交易数</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📋 今日汇总</h2>
            <table>
                <tr>
                    <th>指标</th>
                    <th>数值</th>
                </tr>
                <tr>
                    <td>总信号数</td>
                    <td>{total_signals}</td>
                </tr>
                <tr>
                    <td>总交易数</td>
                    <td>{total_trades}</td>
                </tr>
                <tr>
                    <td>策略配置</td>
                    <td>量化 {config['strategies']['quant_core']['allocation']*100:.0f}% | 天气 {config['strategies']['weather_arb']['allocation']*100:.0f}% | 事件 {config['strategies']['event_trading']['allocation']*100:.0f}%</td>
                </tr>
            </table>
        </div>
        
        <div class="section">
            <h2>⚙️ 策略配置</h2>
            <table>
                <tr>
                    <th>策略</th>
                    <th>状态</th>
                    <th>资金分配</th>
                    <th>扫描频率</th>
                </tr>
                <tr>
                    <td><span class="badge badge-quant">量化核心</span></td>
                    <td>{'🟢 启用' if config['strategies']['quant_core']['enabled'] else '🔴 禁用'}</td>
                    <td>{config['strategies']['quant_core']['allocation']*100:.0f}%</td>
                    <td>{config['strategies']['quant_core']['scan_interval_minutes'] or '手动'}分钟</td>
                </tr>
                <tr>
                    <td><span class="badge badge-weather">天气套利</span></td>
                    <td>{'🟢 启用' if config['strategies']['weather_arb']['enabled'] else '🔴 禁用'}</td>
                    <td>{config['strategies']['weather_arb']['allocation']*100:.0f}%</td>
                    <td>{config['strategies']['weather_arb']['scan_interval_minutes'] or '手动'}分钟</td>
                </tr>
                <tr>
                    <td><span class="badge badge-event">事件交易</span></td>
                    <td>{'🟢 启用' if config['strategies']['event_trading']['enabled'] else '🔴 禁用'}</td>
                    <td>{config['strategies']['event_trading']['allocation']*100:.0f}%</td>
                    <td>{config['strategies']['event_trading']['scan_interval_minutes'] or '手动'}分钟</td>
                </tr>
            </table>
        </div>
        
        <div class="footer">
            <p>Polymarket 统一交易系统 v1.0 | 模拟交易 | 不构成投资建议</p>
            <p>策略：量化核心 (EV/贝叶斯/凯利/KL 散度) + 天气套利 + 事件交易</p>
        </div>
    </div>
</body>
</html>
"""
    return html


def send_email(subject: str, html_content: str, config: dict):
    """发送邮件"""
    email_config = config.get('email', {})
    
    smtp_server = email_config.get('smtp_server', 'smtp.qq.com')
    smtp_port = email_config.get('smtp_port', 465)
    from_email = email_config.get('from', email_config.get('from_email', ''))
    password = email_config.get('password', '')
    to_email = email_config.get('to', email_config.get('to_email', '4352395@qq.com'))
    
    if not password or from_email == '':
        print(f"⚠️  邮箱配置未设置，邮件内容已保存到 drafts/email_draft.html")
        save_draft(html_content)
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # QQ 邮箱 465 端口使用 SSL，587 端口使用 STARTTLS
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
        
        server.login(from_email, password)
        server.sendmail(from_email, [to_email], msg.as_string())
        server.quit()
        
        print(f"✅ 邮件已发送：{to_email}")
        return True
        
    except Exception as e:
        print(f"❌ 邮件发送失败：{e}")
        save_draft(html_content)
        return False


def save_draft(html_content: str):
    """保存邮件草稿"""
    drafts_dir = SCRIPT_DIR / 'drafts'
    drafts_dir.mkdir(exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    draft_file = drafts_dir / f'email_draft_{today}.html'
    
    with open(draft_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"📄 邮件草稿已保存：{draft_file}")


def generate_and_send(quant_result: dict, weather_result: dict, event_result: dict, config: dict):
    """生成并发送邮件报告（只在有真实数据时发送）"""
    # 数据质量检查
    total_signals = (
        len(quant_result.get('signals', [])) + 
        len(weather_result.get('signals', [])) + 
        len(event_result.get('signals', []))
    )
    
    # 检查是否有真实数据
    if total_signals == 0:
        print("📧 无信号数据，跳过邮件发送")
        return
    
    # 检查是否都是模拟数据
    api_source = quant_result.get('details', {}).get('api_source', 'mock')
    if api_source == 'mock' and total_signals < 3:
        print("📧 数据质量不足（模拟数据且信号少），跳过邮件发送")
        return
    
    html_content = generate_html_report(quant_result, weather_result, event_result, config)
    subject = f"🤖 Polymarket 量化机器人每日战报 - {datetime.now().strftime('%Y-%m-%d')}"
    send_email(subject, html_content, config)


if __name__ == "__main__":
    # 测试用
    config = {
        "account": {"initial_capital": 10000},
        "strategies": {
            "quant_core": {"enabled": True, "allocation": 0.4, "scan_interval_minutes": 15},
            "weather_arb": {"enabled": True, "allocation": 0.3, "scan_interval_minutes": None},
            "event_trading": {"enabled": True, "allocation": 0.3, "scan_interval_minutes": None}
        }
    }
    generate_and_send(
        {"signals": [1,2,3], "trades": 2},
        {"signals": [1,2], "trades": 1},
        {"signals": [1], "trades": 0},
        config
    )
