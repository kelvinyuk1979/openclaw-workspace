#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全天交易复盘邮件 - 工作日每天 5PM 发送
包含：OKX 量化 + Polymarket + A 股全天总结
"""

import smtplib
import json
import sys
from pathlib import Path
from datetime import datetime
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

WORKSPACE = Path(__file__).parent.parent
OKX_DIR = WORKSPACE / 'skills' / 'stock-market-pro' / 'quant-trading-system'

def load_json(path, default=None):
    """加载 JSON 文件，失败返回默认值"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return default if default else {}

def get_okx_data():
    """获取 OKX 数据 - 适配实际数据格式"""
    account = load_json(OKX_DIR / 'data' / 'account.json', {})
    positions_raw = load_json(OKX_DIR / 'data' / 'positions.json', {})
    signals = load_json(OKX_DIR / 'logs' / 'latest_signals.json', {"signals": []})
    
    # 从 account.json 获取持仓（实际格式）
    positions_list = account.get('positions', [])
    
    # 计算总盈亏
    total_pnl = account.get('total_pnl', 0)
    starting = account.get('initial_capital', 143.85)
    balance = account.get('balance', 0)
    pnl_pct = ((balance - starting) / starting) * 100 if starting else 0
    
    # 转换持仓格式
    positions_display = []
    for p in positions_list:
        if isinstance(p, dict):
            positions_display.append({
                'instId': p.get('symbol', '') + '-SWAP',
                'posSide': p.get('side', ''),
                'pos': p.get('amount', 0),
                'upl': p.get('pnl_pct', 0)  # 用 pnl_pct 代替 upl
            })
    
    return {
        "balance": balance + total_pnl,  # 总权益
        "available": float(account.get('balance', 0)),  # 可用余额
        "pnl": total_pnl,
        "pnl_pct": pnl_pct,
        "positions": positions_display,
        "signals": signals.get("signals", [])
    }

def get_ashare_summary():
    """获取 A 股全天总结"""
    import urllib.request
    
    INDEX_CODES = "sh000001,sz399001,sz399006,sh000688"
    
    def _fetch(codes_str):
        url = f"http://qt.gtimg.cn/q={codes_str}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10)
        raw = resp.read()
        try:
            text = raw.decode('gbk')
        except:
            text = raw.decode('utf-8', errors='ignore')
        items = []
        for line in text.strip().split(';'):
            if '~' not in line: continue
            p = line.split('~')
            if len(p) < 35: continue
            try:
                items.append({
                    "code": p[2], "name": p[1],
                    "price": float(p[3]) if p[3] else 0,
                    "change": float(p[32]) if len(p) > 32 and p[32] else 0,
                })
            except:
                continue
        return items
    
    try:
        indices = _fetch(INDEX_CODES)
        return {"source": "live", "indices": indices}
    except:
        return {"source": "unavailable", "indices": []}

def generate_recap_content():
    """生成复盘邮件内容"""
    okx = get_okx_data()
    ashare = get_ashare_summary()
    today = datetime.now().strftime('%Y-%m-%d')
    
    html = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
        h1 {{ color: #333; border-bottom: 3px solid #00ba7c; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; padding: 15px 25px; background: #f8f9fa; border-radius: 8px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #333; }}
        .metric-label {{ font-size: 12px; color: #888; margin-top: 5px; }}
        .positive {{ color: #00ba7c; }}
        .negative {{ color: #f4212e; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #f8f9fa; font-weight: 600; }}
        .card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; color: #888; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 全天交易复盘 - {today}</h1>
        
        <!-- OKX 量化 -->
        <h2>₿ OKX 加密货币量化</h2>
        <div class="card">
            <div class="metric">
                <div class="metric-value">${okx['balance']:.2f}</div>
                <div class="metric-label">总权益</div>
            </div>
            <div class="metric">
                <div class="metric-value">${okx['available']:.2f}</div>
                <div class="metric-label">可用</div>
            </div>
            <div class="metric">
                <div class="metric-value {{ 'positive' if okx['pnl'] >= 0 else 'negative' }}">
                    ${okx['pnl']:+.2f}
                </div>
                <div class="metric-label">今日盈亏</div>
            </div>
            <div class="metric">
                <div class="metric-value {{ 'positive' if okx['pnl_pct'] >= 0 else 'negative' }}">
                    {okx['pnl_pct']:+.2f}%
                </div>
                <div class="metric-label">总收益率</div>
            </div>
        </div>
        
        {f'''
        <h3>📈 持仓状态</h3>
        <table>
            <tr><th>币种</th><th>方向</th><th>数量</th><th>未实现盈亏</th></tr>
            {"".join(f"<tr><td>{p.get('instId','').replace('-SWAP','')}</td><td>{p.get('posSide','')}</td><td>{p.get('pos','0')}</td><td class=\"{'positive' if float(p.get('upl',0) or 0) >= 0 else 'negative'}\">${float(p.get('upl',0) or 0):.2f}</td></tr>" for p in okx['positions'] if isinstance(p, dict)) if okx['positions'] else '<tr><td colspan="4">无持仓</td></tr>'}
        </table>
        ''' if okx['positions'] else ''}
        
        <!-- A 股总结 -->
        <h2>📈 A 股收盘总结</h2>
        <div class="card">
            {f'''
            <table>
                <tr><th>指数</th><th>收盘点位</th><th>涨跌幅</th></tr>
                {"".join(f"<tr><td>{i['name']}</td><td>{i['price']:,.2f}</td><td class=\"{'positive' if i['change'] >= 0 else 'negative'}\">{i['change']:+.2f}%</td></tr>" for i in ashare.get('indices', [])) if ashare.get('indices') else '<tr><td colspan="3">数据不可用</td></tr>'}
            </table>
            ''' if ashare.get('indices') else '<p>A 股数据获取失败</p>'}
        </div>
        
        <div class="footer">
            <p>发送时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>系统状态：OKX ✅ | A 股 {'✅' if ashare.get('source') == 'live' else '⚠️'}</p>
        </div>
    </div>
</body>
</html>
"""
    return html

def send_email(subject, html_content):
    """发送邮件"""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_CONFIG["from_email"]
    msg["To"] = EMAIL_CONFIG["to_email"]
    
    msg.attach(MIMEText(html_content, "html", "utf-8"))
    
    try:
        server = smtplib.SMTP_SSL(
            EMAIL_CONFIG["smtp_server"],
            EMAIL_CONFIG["smtp_port"],
            timeout=30
        )
        server.login(
            EMAIL_CONFIG["from_email"],
            EMAIL_CONFIG["password"]
        )
        server.sendmail(
            EMAIL_CONFIG["from_email"],
            EMAIL_CONFIG["to_email"],
            msg.as_string()
        )
        server.quit()
        print(f"✅ 复盘邮件发送成功：{subject}")
        return True
    except Exception as e:
        print(f"❌ 邮件发送失败：{e}")
        return False

if __name__ == "__main__":
    html = generate_recap_content()
    today = datetime.now().strftime('%Y-%m-%d')
    send_email(f"📊 全天交易复盘 - {today}", html)
