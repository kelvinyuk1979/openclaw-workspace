#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股统一交易系统 - 每日邮件报告
"""

import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent


def generate_html_report(technical: dict, fundamental: dict, sentiment: dict, config: dict) -> str:
    """生成 HTML 报告"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 汇总统计
    total_signals = (
        len(technical.get('signals', [])) + 
        len(fundamental.get('signals', [])) + 
        len(sentiment.get('signals', []))
    )
    total_trades = (
        technical.get('trades', 0) + 
        fundamental.get('trades', 0) + 
        sentiment.get('trades', 0)
    )
    
    # 账户概览
    sim_file = SCRIPT_DIR / 'simulation.json'
    if sim_file.exists():
        with open(sim_file, 'r', encoding='utf-8') as f:
            sim_data = json.load(f)
    else:
        sim_data = {"balance": 100000, "starting_balance": 100000}
    
    balance = sim_data.get('balance', 100000)
    starting = sim_data.get('starting_balance', 100000)
    pnl = balance - starting
    pnl_pct = (pnl / starting * 100) if starting > 0 else 0
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .section {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .section h2 {{ color: #dc2626; margin-top: 0; font-size: 18px; border-bottom: 2px solid #dc2626; padding-bottom: 10px; }}
        .strategy-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 15px 0; }}
        .strategy-card {{ background: #f9fafb; padding: 15px; border-radius: 8px; text-align: center; }}
        .strategy-card h3 {{ margin: 0 0 10px; font-size: 16px; color: #dc2626; }}
        .metric {{ display: inline-block; margin: 10px 15px 10px 0; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #dc2626; }}
        .metric-label {{ font-size: 13px; color: #666; }}
        .positive {{ color: #059669; }}
        .negative {{ color: #dc2626; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
        th {{ background: #dc2626; color: white; }}
        .badge {{ display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
        .badge-tech {{ background: #2563eb; color: white; }}
        .badge-fund {{ background: #059669; color: white; }}
        .badge-sent {{ background: #d97706; color: white; }}
        .badge-buy {{ background: #059669; color: white; }}
        .badge-sell {{ background: #dc2626; color: white; }}
        .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 A 股统一交易系统 - 每日报告</h1>
            <p>报告日期：{today}</p>
        </div>
        
        <div class="section">
            <h2>💰 账户概览</h2>
            <div class="metric">
                <div class="metric-value">¥{balance:,.2f}</div>
                <div class="metric-label">当前余额</div>
            </div>
            <div class="metric">
                <div class="metric-value">¥{pnl:+,.2f}</div>
                <div class="metric-label">总盈亏</div>
            </div>
            <div class="metric">
                <div class="metric-value {'positive' if pnl >= 0 else 'negative'}">{pnl_pct:+.2f}%</div>
                <div class="metric-label">收益率</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 策略表现</h2>
            <div class="strategy-grid">
                <div class="strategy-card">
                    <h3>📈 技术面</h3>
                    <div class="metric">
                        <div class="metric-value">{len(technical.get('signals', []))}</div>
                        <div class="metric-label">信号数</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{technical.get('trades', 0)}</div>
                        <div class="metric-label">交易数</div>
                    </div>
                </div>
                <div class="strategy-card">
                    <h3>💰 基本面</h3>
                    <div class="metric">
                        <div class="metric-value">{len(fundamental.get('signals', []))}</div>
                        <div class="metric-label">信号数</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{fundamental.get('trades', 0)}</div>
                        <div class="metric-label">交易数</div>
                    </div>
                </div>
                <div class="strategy-card">
                    <h3>📰 情绪面</h3>
                    <div class="metric">
                        <div class="metric-value">{len(sentiment.get('signals', []))}</div>
                        <div class="metric-label">信号数</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{sentiment.get('trades', 0)}</div>
                        <div class="metric-label">交易数</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🎯 Top 信号</h2>
            <table>
                <tr>
                    <th>策略</th>
                    <th>代码</th>
                    <th>名称</th>
                    <th>信号</th>
                    <th>原因</th>
                </tr>
"""
    
    # 合并所有信号
    all_signals = []
    for sig in technical.get('signals', [])[:3]:
        sig['strategy'] = 'Technical'
        all_signals.append(sig)
    for sig in fundamental.get('signals', [])[:3]:
        sig['strategy'] = 'Fundamental'
        all_signals.append(sig)
    for sig in sentiment.get('signals', [])[:3]:
        sig['strategy'] = 'Sentiment'
        all_signals.append(sig)
    
    for sig in all_signals[:10]:
        badge_class = 'badge-tech' if sig.get('strategy') == 'Technical' else ('badge-fund' if sig.get('strategy') == 'Fundamental' else 'badge-sent')
        signal_class = 'badge-buy' if sig.get('signal') == 'BUY' else 'badge-sell'
        
        html += f"""
                <tr>
                    <td><span class="badge {badge_class}">{sig.get('strategy', 'N/A')}</span></td>
                    <td>{sig.get('code', 'N/A')}</td>
                    <td>{sig.get('name', 'N/A')}</td>
                    <td><span class="badge {signal_class}">{sig.get('signal', 'N/A')}</span></td>
                    <td>{sig.get('reason', 'N/A')}</td>
                </tr>
"""
    
    html += f"""
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
"""
    
    for name, cfg in config.get('strategies', {}).items():
        name_cn = {'technical': '技术面', 'fundamental': '基本面', 'sentiment': '情绪面'}.get(name, name)
        html += f"""
                <tr>
                    <td>{name_cn}</td>
                    <td>{'🟢 启用' if cfg.get('enabled') else '🔴 禁用'}</td>
                    <td>{cfg.get('allocation', 0)*100:.0f}%</td>
                    <td>{cfg.get('scan_interval_minutes') or '手动'} 分钟</td>
                </tr>
"""
    
    html += f"""
            </table>
        </div>
        
        <div class="footer">
            <p>A 股统一交易系统 v1.0 | 模拟交易 | 不构成投资建议</p>
            <p>策略：技术面 (MA/MACD/RSI) + 基本面 (PE/ROE/增长) + 情绪面 (新闻/资金流)</p>
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
    from_email = email_config.get('from', '')
    password = email_config.get('password', '')
    to_email = email_config.get('to', '4352395@qq.com')
    
    if not password or from_email == '':
        print(f"⚠️  邮箱配置未设置")
        save_draft(html_content)
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
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


def generate_and_send(technical: dict, fundamental: dict, sentiment: dict, config: dict):
    """生成并发送邮件报告（只在有真实数据时发送）"""
    # 数据质量检查
    total_signals = (
        len(technical.get('signals', [])) + 
        len(fundamental.get('signals', [])) + 
        len(sentiment.get('signals', []))
    )
    
    # 检查是否有真实数据
    if total_signals == 0:
        print("📧 无信号数据，跳过邮件发送")
        return
    
    # 检查数据源质量
    data_source = technical.get('details', {}).get('data_source', 'mock')
    if data_source == 'mock' and total_signals < 3:
        print("📧 数据质量不足（模拟数据且信号少），跳过邮件发送")
        return
    
    html_content = generate_html_report(technical, fundamental, sentiment, config)
    subject = f"📈 A 股量化机器人每日战报 - {datetime.now().strftime('%Y-%m-%d')}"
    send_email(subject, html_content, config)


if __name__ == "__main__":
    # 测试用
    config = {
        "email": {"to": "4352395@qq.com", "from": "4352395@qq.com", "password": "test"}
    }
    generate_and_send(
        {"signals": [{"code": "600519", "name": "贵州茅台", "signal": "BUY", "reason": "RSI 超卖"}], "trades": 1},
        {"signals": [{"code": "002594", "name": "比亚迪", "signal": "BUY", "reason": "高增长"}], "trades": 1},
        {"signals": [{"code": "300750", "name": "宁德时代", "signal": "SELL", "reason": "资金流出"}], "trades": 1},
        config
    )
