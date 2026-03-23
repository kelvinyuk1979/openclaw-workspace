#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 三系统统一每日战报 - 邮件发送
Polymarket + A 股 + OKX 加密货币
"""

import json
import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).parent
POLY_DIR = WORKSPACE / 'polymarket-trading-system'
ASHARE_DIR = WORKSPACE / 'a-share-trading-system'
OKX_DIR = WORKSPACE / 'okx-trading-system'

def load_json(path, default=None):
    """加载 JSON 文件"""
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default or {}

def get_system_status():
    """获取三个系统状态"""
    # Polymarket
    poly_sim = load_json(POLY_DIR / 'simulation.json', {"balance": 10000, "starting_balance": 10000})
    poly_pnl = poly_sim.get('balance', 10000) - poly_sim.get('starting_balance', 10000)
    poly_pnl_pct = (poly_pnl / poly_sim.get('starting_balance', 10000)) * 100
    
    # A 股
    ashare_sim = load_json(ASHARE_DIR / 'simulation.json', {"balance": 100000, "starting_balance": 100000})
    ashare_pnl = ashare_sim.get('balance', 100000) - ashare_sim.get('starting_balance', 100000)
    ashare_pnl_pct = (ashare_pnl / ashare_sim.get('starting_balance', 100000)) * 100
    
    # OKX
    okx_account = load_json(OKX_DIR / 'data' / 'account.json', {"balance": 10000, "initial_capital": 10000, "total_pnl": 0})
    okx_pnl = okx_account.get('total_pnl', 0)
    okx_pnl_pct = (okx_pnl / okx_account.get('initial_capital', 10000)) * 100
    okx_positions = load_json(OKX_DIR / 'data' / 'positions.json', {})
    
    return {
        'polymarket': {
            'balance': poly_sim.get('balance', 10000),
            'pnl': poly_pnl,
            'pnl_pct': poly_pnl_pct,
            'currency': 'USDC'
        },
        'ashare': {
            'balance': ashare_sim.get('balance', 100000),
            'pnl': ashare_pnl,
            'pnl_pct': ashare_pnl_pct,
            'currency': 'CNY'
        },
        'okx': {
            'balance': okx_account.get('balance', 10000),
            'pnl': okx_pnl,
            'pnl_pct': okx_pnl_pct,
            'currency': 'USDT',
            'positions_count': len(okx_positions)
        }
    }

def get_latest_signals():
    """获取最新信号"""
    # OKX 信号
    okx_signals = load_json(OKX_DIR / 'logs' / 'latest_signals.json', {"signals": []})
    
    # A 股信号
    ashare_scan = load_json(ASHARE_DIR / 'logs' / 'latest_scan.json', {"results": {}})
    
    # Polymarket 信号
    poly_scan = load_json(POLY_DIR / 'logs' / 'latest_scan.json', {"results": {}})
    
    return {
        'okx': okx_signals.get('signals', [])[:5],
        'ashare': {
            'technical': ashare_scan.get('results', {}).get('technical', {}).get('signals', [])[:3],
            'fundamental': ashare_scan.get('results', {}).get('fundamental', {}).get('signals', [])[:3]
        },
        'polymarket': {
            'quant': poly_scan.get('results', {}).get('quant', {}).get('signals', [])[:3],
            'weather': poly_scan.get('results', {}).get('weather', {}).get('signals', [])[:3]
        }
    }

def send_email(subject, html_content, email_config):
    """发送邮件"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = email_config['from']
        msg['To'] = email_config['to']
        
        # HTML 版本
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # 连接 SMTP 服务器
        server = smtplib.SMTP_SSL(email_config['smtp_server'], email_config['smtp_port'])
        server.login(email_config['from'], email_config['password'])
        server.sendmail(email_config['from'], email_config['to'], msg.as_string())
        server.quit()
        
        print(f"✅ 邮件已发送：{email_config['to']}")
        return True
    except Exception as e:
        print(f"❌ 邮件发送失败：{e}")
        return False

def generate_report(period="上午"):
    """生成战报 HTML"""
    status = get_system_status()
    signals = get_latest_signals()
    
    total_pnl_usd = status['polymarket']['pnl'] + status['okx']['pnl']
    
    # 计算总收益率（简化）
    total_invested = 10000 + 10000  # Polymarket + OKX (USDT/USDC)
    total_pnl_pct = (total_pnl_usd / total_invested) * 100 if total_invested > 0 else 0
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0 0 10px 0; font-size: 28px; }}
        .header p {{ margin: 0; opacity: 0.9; }}
        .summary {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1px; background: #e0e0e0; }}
        .summary-card {{ background: white; padding: 20px; text-align: center; }}
        .summary-card h3 {{ margin: 0 0 10px 0; color: #666; font-size: 14px; }}
        .summary-card .value {{ font-size: 28px; font-weight: bold; margin-bottom: 5px; }}
        .positive {{ color: #00ba7c; }}
        .negative {{ color: #f4212e; }}
        .section {{ padding: 20px; border-bottom: 1px solid #eee; }}
        .section h2 {{ margin: 0 0 15px 0; color: #333; font-size: 18px; display: flex; align-items: center; gap: 8px; }}
        .system-row {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-bottom: 15px; }}
        .system-card {{ background: #f8f9fa; border-radius: 8px; padding: 15px; }}
        .system-card h4 {{ margin: 0 0 10px 0; color: #333; }}
        .metric {{ display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #eee; font-size: 14px; }}
        .metric:last-child {{ border-bottom: none; }}
        .signals-list {{ list-style: none; padding: 0; }}
        .signals-list li {{ background: #f8f9fa; margin: 8px 0; padding: 10px; border-radius: 6px; font-size: 13px; }}
        .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; margin-left: 5px; }}
        .badge-buy {{ background: #00ba7c; color: white; }}
        .badge-sell {{ background: #f4212e; color: white; }}
        .badge-hold {{ background: #5c6b7f; color: white; }}
        .footer {{ background: #f8f9fa; padding: 15px; text-align: center; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 量化交易每日战报</h1>
            <p>{period}版 · {now}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>总盈亏 (USD)</h3>
                <div class="value {'positive' if total_pnl_usd >= 0 else 'negative'}">${total_pnl_usd:+,.0f}</div>
            </div>
            <div class="summary-card">
                <h3>总收益率</h3>
                <div class="value {'positive' if total_pnl_pct >= 0 else 'negative'}">{total_pnl_pct:+.2f}%</div>
            </div>
            <div class="summary-card">
                <h3>OKX 持仓</h3>
                <div class="value">{status['okx']['positions_count']}</div>
            </div>
        </div>
        
        <div class="section">
            <h2>💰 系统详情</h2>
            <div class="system-row">
                <div class="system-card">
                    <h4>🤖 Polymarket</h4>
                    <div class="metric"><span>余额</span><strong>${status['polymarket']['balance']:,.0f}</strong></div>
                    <div class="metric"><span>盈亏</span><span class="{'positive' if status['polymarket']['pnl'] >= 0 else 'negative'}">${status['polymarket']['pnl']:+,.0f}</span></div>
                    <div class="metric"><span>收益率</span><span class="{'positive' if status['polymarket']['pnl_pct'] >= 0 else 'negative'}">{status['polymarket']['pnl_pct']:+.2f}%</span></div>
                </div>
                <div class="system-card">
                    <h4>📈 A 股</h4>
                    <div class="metric"><span>余额</span><strong>¥{status['ashare']['balance']:,.0f}</strong></div>
                    <div class="metric"><span>盈亏</span><span class="{'positive' if status['ashare']['pnl'] >= 0 else 'negative'}">¥{status['ashare']['pnl']:+,.0f}</span></div>
                    <div class="metric"><span>收益率</span><span class="{'positive' if status['ashare']['pnl_pct'] >= 0 else 'negative'}">{status['ashare']['pnl_pct']:+.2f}%</span></div>
                </div>
                <div class="system-card">
                    <h4>₿ OKX</h4>
                    <div class="metric"><span>余额</span><strong>${status['okx']['balance']:,.0f}</strong></div>
                    <div class="metric"><span>盈亏</span><span class="{'positive' if status['okx']['pnl'] >= 0 else 'negative'}">${status['okx']['pnl']:+,.0f}</span></div>
                    <div class="metric"><span>收益率</span><span class="{'positive' if status['okx']['pnl_pct'] >= 0 else 'negative'}">{status['okx']['pnl_pct']:+.2f}%</span></div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📡 最新信号</h2>
            <h3>OKX 加密货币</h3>
            <ul class="signals-list">
"""
    
    # OKX 信号
    for sig in signals['okx'][:5]:
        badge_class = 'buy' if sig.get('signal') == 'LONG' else ('sell' if sig.get('signal') == 'SHORT' else 'hold')
        symbol = sig.get('symbol', 'N/A').replace('-USDT', '')
        rsi = sig.get('indicators', {}).get('rsi', 'N/A')
        html += f"""<li><strong>{symbol}</strong> - {sig.get('signal', 'HOLD')} <span class="badge badge-{badge_class}">{sig.get('signal', 'HOLD')}</span><br>RSI: {rsi} | L:{sig.get('votes', {}).get('long', 0)} S:{sig.get('votes', {}).get('short', 0)} H:{sig.get('votes', {}).get('hold', 0)}</li>"""
    
    if not signals['okx']:
        html += "<li>暂无信号</li>"
    
    html += """
            </ul>
        </div>
        
        <div class="footer">
            <p>此邮件由量化交易系统自动生成 · 模拟交易数据仅供参考</p>
            <p>Polymarket + A 股 + OKX 统一监控</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html

def main():
    period = sys.argv[1] if len(sys.argv) > 1 else "上午"
    
    # 获取 OKX 邮箱配置
    okx_config = load_json(OKX_DIR / 'config' / 'config.json', {})
    email_config = okx_config.get('email', {})
    
    if not email_config.get('enabled'):
        print("❌ 邮件功能未启用")
        sys.exit(1)
    
    # 生成并发送邮件
    subject = f"📊 量化交易每日战报 - {period}版 ({datetime.now().strftime('%Y-%m-%d')})"
    html = generate_report(period)
    
    success = send_email(subject, html, email_config)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
