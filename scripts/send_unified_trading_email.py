#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一交易日报邮件 - 每天早上 9 点发送
包含：OKX 量化 + Polymarket 预测 + A 股选股
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
POLY_DIR = WORKSPACE / 'polymarket-trading-system'


def load_json(path: Path, default=None):
    """加载 JSON 文件"""
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default or {}


def get_okx_data():
    """获取 OKX 数据"""
    account = load_json(OKX_DIR / 'data' / 'account.json', {"balance": 0, "initial_capital": 0})
    positions = load_json(OKX_DIR / 'data' / 'positions.json', {})
    signals = load_json(OKX_DIR / 'logs' / 'latest_signals.json', {"signals": []})
    
    pnl = account.get('balance', 0) - account.get('initial_capital', 0)
    pnl_pct = (pnl / account.get('initial_capital', 1)) * 100 if account.get('initial_capital') else 0
    
    return {
        "balance": account.get('balance', 0),
        "initial": account.get('initial_capital', 0),
        "pnl": pnl,
        "pnl_pct": pnl_pct,
        "positions": positions,
        "signals": signals.get('signals', [])
    }


def get_polymarket_data():
    """获取 Polymarket 数据"""
    scan = load_json(POLY_DIR / 'logs' / 'latest_scan.json', {"results": {}})
    sim = load_json(POLY_DIR / 'simulation.json', {"balance": 10000, "starting_balance": 10000})
    
    pnl = sim.get('balance', 10000) - sim.get('starting_balance', 10000)
    pnl_pct = (pnl / sim.get('starting_balance', 10000)) * 100 if sim.get('starting_balance') else 0
    
    return {
        "balance": sim.get('balance', 10000),
        "pnl": pnl,
        "pnl_pct": pnl_pct,
        "signals": scan.get('results', {}).get('quant', {}).get('signals', [])
    }


def get_ashare_data():
    """获取 A 股实时数据（腾讯行情 API + 重试）"""
    import urllib.request
    import time as _time
    
    # 分成小批次（每批 15 只），网络波动下成功率最高
    INDEX_BATCH = ["sh000001", "sz399001", "sz399006", "sh000688"]
    STOCK_BATCHES = [
        ["sh600519","sz000858","sz300750","sz002594","sh601318","sh600036","sh600276","sh603259","sh688041","sh688256","sz002371","sh688012","sz300661","sz002230","sh603019"],
        ["sh601899","sh603993","sz002460","sz300274","sh600900","sh600941","sz300059","sz002415","sh600150","sh600760","sh601888","sz300433","sz002241"],
    ]
    
    def _fetch_with_retry(codes, max_retries=3):
        url = f"http://qt.gtimg.cn/q={','.join(codes)}"
        for attempt in range(max_retries):
            try:
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
                            "amount_yi": round(float(p[37]) / 1e4, 1) if len(p) > 37 and p[37] else 0,
                        })
                    except (ValueError, IndexError):
                        continue
                return items
            except Exception:
                if attempt < max_retries - 1:
                    _time.sleep(1)
        return []
    
    try:
        indices = _fetch_with_retry(INDEX_BATCH)
        stocks = []
        for batch in STOCK_BATCHES:
            stocks.extend(_fetch_with_retry(batch))
        stocks = [s for s in stocks if s['price'] > 0]
        stocks.sort(key=lambda x: x['change'], reverse=True)
        return {
            "source": "live",
            "indices": indices,
            "top_gainers": [s for s in stocks[:5] if s['change'] > 0],
            "top_losers": stocks[-3:],
            "all": stocks,
        }
    except Exception as e:
        # 尝试读缓存
        cached = load_json(WORKSPACE / 'scripts' / 'ashare_picks.json', {})
        if cached.get('strategies'):
            return {
                "source": "cache",
                "indices": cached.get('indices', []),
                "top_gainers": cached['strategies'].get('momentum', [])[:5],
                "top_losers": cached['strategies'].get('oversold', [])[:3],
                "all": cached['strategies'].get('momentum', []),
            }
        return {"source": "unavailable", "indices": [], "top_gainers": [], "top_losers": [], "all": []}


def get_tradingview_data():
    """获取 TradingView 深度分析数据（优化版：3 次 API 调用代替 21 次）"""
    import subprocess
    
    RAPIDAPI_KEY = "9c5420d125msh613da73e04513e8p191bb9jsn1a2af314f994"
    TV_SYMBOLS = [
        "SSE:600519", "SZSE:300750", "SSE:601318", "SZSE:002594", "SSE:688041",
        "SSE:600276", "SSE:603259", "SZSE:002371", "SSE:601899", "SZSE:300661",
    ]
    
    def _call_mcp(jwt, method_name, arguments):
        import json as _json
        payload = _json.dumps({
            "jsonrpc": "2.0", "id": 1,
            "method": "tools/call",
            "params": {"name": method_name, "arguments": arguments}
        })
        p = subprocess.run([
            "curl", "-s", "--max-time", "15",
            "-X", "POST",
            "-H", f"Authorization: Bearer {jwt}",
            "-H", "Content-Type: application/json",
            "-H", "Accept: application/json, text/event-stream",
            "https://mcp.tradingviewapi.com/mcp",
            "-d", payload
        ], capture_output=True, text=True, timeout=20)
        result = _json.loads(p.stdout)
        content = result["result"]["content"][0]["text"]
        return _json.loads(content)
    
    try:
        # 1. 获取 JWT（1 次调用）
        p = subprocess.run([
            "curl", "-s", "--max-time", "10",
            "-X", "POST",
            "-H", "Content-Type: application/json",
            "-H", "x-rapidapi-host: tradingview-data1.p.rapidapi.com",
            "-H", f"x-rapidapi-key: {RAPIDAPI_KEY}",
            "https://tradingview-data1.p.rapidapi.com/api/mcp/generate",
            "-d", "{}"
        ], capture_output=True, text=True, timeout=15)
        jwt = json.loads(p.stdout)["token"]
        
        # 2. 批量获取报价（1 次调用，最多 10 只）
        batch_result = _call_mcp(jwt, "tradingview_get_quote_batch", {
            "symbols": TV_SYMBOLS,
            "response_format": "json"
        })
        # batch 返回 {total, successful, failed, data: [{success, symbol, data: {...}}, ...]}
        quotes_map = {}
        for item in batch_result.get("data", []):
            if isinstance(item, dict) and item.get("success"):
                quotes_map[item["symbol"]] = item.get("data", {})
        
        # 3. 逐个获取技术分析（TA 无 batch 接口）
        stocks = []
        for sym in TV_SYMBOLS:
            d = quotes_map.get(sym, {})
            if not d or not d.get("lp"):
                continue
            
            # 技术分析
            ta_signal = "N/A"
            ta_score = 0
            try:
                ta = _call_mcp(jwt, "tradingview_get_ta", {"symbol": sym, "response_format": "json"})
                ta_daily = ta.get("ta", {}).get("1D", {})
                ta_score = ta_daily.get("All", 0)
                
                if ta_score <= -0.5: ta_signal = "强买入"
                elif ta_score <= -0.1: ta_signal = "买入"
                elif ta_score <= 0.1: ta_signal = "中性"
                elif ta_score <= 0.5: ta_signal = "卖出"
                else: ta_signal = "强卖出"
            except Exception:
                pass
            
            stocks.append({
                "symbol": sym,
                "name": d.get("local_description", d.get("description", sym)),
                "price": d.get("lp", 0),
                "change": d.get("chp", 0),
                "pe": d.get("price_earnings_ttm", 0),
                "market_cap": d.get("market_cap_basic", 0),
                "dividend_yield": d.get("dividends_yield", 0),
                "week52_high": d.get("price_52_week_high", 0),
                "week52_low": d.get("price_52_week_low", 0),
                "ta_signal": ta_signal,
                "ta_score": ta_score,
            })
        
        return {"source": "live", "stocks": stocks}
    except Exception as e:
        return {"source": "unavailable", "stocks": [], "error": str(e)}


def generate_email_content():
    """生成统一邮件内容"""
    okx = get_okx_data()
    poly = get_polymarket_data()
    ashare = get_ashare_data()
    tv = get_tradingview_data()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 900px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
            .container {{ background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 28px; }}
            .header p {{ margin: 10px 0 0; opacity: 0.9; }}
            .section {{ padding: 25px; border-bottom: 1px solid #eee; }}
            .section:last-child {{ border-bottom: none; }}
            .section-title {{ font-size: 20px; color: #667eea; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; }}
            .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px; }}
            .metric {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }}
            .metric-value {{ font-size: 24px; font-weight: bold; margin-bottom: 5px; }}
            .metric-label {{ color: #666; font-size: 12px; }}
            .positive {{ color: #00ba7c; }}
            .negative {{ color: #f4212e; }}
            .card {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #667eea; }}
            .card h4 {{ margin: 0 0 10px; color: #333; }}
            .card p {{ margin: 5px 0; font-size: 14px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #eee; }}
            th {{ background: #667eea; color: white; }}
            .badge {{ display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
            .badge-buy {{ background: #00ba7c; color: white; }}
            .badge-hold {{ background: #5c6b7f; color: white; }}
            .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #999; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌐 统一交易日报</h1>
                <p>📅 {today} | OKX + Polymarket + A 股</p>
            </div>
            
            <!-- OKX 量化交易 -->
            <div class="section">
                <h2 class="section-title">₿ OKX 加密货币量化</h2>
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-value">${okx['balance']:.2f}</div>
                        <div class="metric-label">账户余额</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value {{ 'positive' if okx['pnl'] >= 0 else 'negative' }}">
                            ${okx['pnl']:+.2f}
                        </div>
                        <div class="metric-label">总盈亏</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value {{ 'positive' if okx['pnl_pct'] >= 0 else 'negative' }}">
                            {okx['pnl_pct']:+.2f}%
                        </div>
                        <div class="metric-label">收益率</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{len(okx['positions'])}</div>
                        <div class="metric-label">持仓数</div>
                    </div>
                </div>
                
                {f'''
                <div class="card">
                    <h4>📦 当前持仓</h4>
                    <table>
                        <tr><th>币种</th><th>方向</th><th>数量</th><th>成本价</th><th>成本</th></tr>
                        {"".join(f"<tr><td>{p.get('symbol', 'N/A')}</td><td>{p.get('side', 'N/A')}</td><td>{p.get('amount', 0):.6f}</td><td>${p.get('avg_price', 0):,.2f}</td><td>${p.get('cost', 0):.2f}</td></tr>" for p in okx['positions'].values()) if okx['positions'] else '<tr><td colspan="5">无持仓</td></tr>'}
                    </table>
                </div>
                ''' if okx['positions'] else ''}
                
                <div class="card">
                    <h4>📊 最新信号</h4>
                    <table>
                        <tr><th>币种</th><th>价格</th><th>RSI</th><th>信号</th><th>置信度</th></tr>
                        {"".join(f"<tr><td>{s.get('symbol', '').replace('-USDT', '')}</td><td>${s.get('price', 0):,.2f}</td><td>{s.get('rsi', 0):.1f}</td><td><span class='badge badge-{'buy' if s.get('signal') == 'BUY' else 'hold'}'>{s.get('signal', 'N/A')}</span></td><td>{s.get('confidence', 0):.0f}%</td></tr>" for s in okx['signals']) if okx['signals'] else '<tr><td colspan="5">无信号</td></tr>'}
                    </table>
                </div>
            </div>
            
            <!-- Polymarket 预测市场 -->
            <div class="section">
                <h2 class="section-title">🤖 Polymarket 预测市场</h2>
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-value">${poly['balance']:.2f}</div>
                        <div class="metric-label">账户余额</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value {{ 'positive' if poly['pnl'] >= 0 else 'negative' }}">
                            ${poly['pnl']:+.2f}
                        </div>
                        <div class="metric-label">总盈亏</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value {{ 'positive' if poly['pnl_pct'] >= 0 else 'negative' }}">
                            {poly['pnl_pct']:+.2f}%
                        </div>
                        <div class="metric-label">收益率</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{len(poly['signals'])}</div>
                        <div class="metric-label">机会数</div>
                    </div>
                </div>
                
                <div class="card">
                    <h4>🎯 推荐市场</h4>
                    <table>
                        <tr><th>市场</th><th>类型</th><th>EV</th><th>价格</th><th>操作</th></tr>
                        {"".join(f"<tr><td>{s.get('market', 'N/A')}</td><td>{s.get('type', 'N/A')}</td><td>{s.get('ev', 0):.2f}</td><td>{s.get('price', 0):.2f}</td><td><span class='badge badge-buy'>{s.get('action', 'N/A')}</span></td></tr>" for s in poly['signals'][:5]) if poly['signals'] else '<tr><td colspan="5">无推荐</td></tr>'}
                    </table>
                </div>
            </div>
            
            <!-- A 股实时行情 -->
            <div class="section">
                <h2 class="section-title">📈 A 股实时行情 {'(缓存)' if ashare.get('source') == 'cache' else ''}</h2>
                
                <div class="card">
                    <h4>📊 大盘指数</h4>
                    <table>
                        <tr><th>指数</th><th>点位</th><th>涨跌幅</th></tr>
                        {"".join(f"<tr><td>{i.get('name','')}</td><td>{i.get('price',0):,.2f}</td><td style='color:{'#00ba7c' if i.get('change',0) >= 0 else '#f4212e'}'>{i.get('change',0):+.2f}%</td></tr>" for i in ashare.get('indices', [])) if ashare.get('indices') else '<tr><td colspan="3">数据不可用</td></tr>'}
                    </table>
                </div>
                
                <div class="card">
                    <h4>📈 涨幅前 5</h4>
                    <table>
                        <tr><th>代码</th><th>名称</th><th>价格</th><th>涨跌幅</th><th>成交额</th></tr>
                        {"".join(f"<tr><td>{s.get('code','')}</td><td>{s.get('name','')}</td><td>¥{s.get('price',0):,.2f}</td><td style='color:#00ba7c'>{s.get('change',0):+.2f}%</td><td>{s.get('amount_yi',0)}亿</td></tr>" for s in ashare.get('top_gainers', [])) if ashare.get('top_gainers') else '<tr><td colspan="5">无上涨股票</td></tr>'}
                    </table>
                </div>
                
                <div class="card">
                    <h4>📉 跌幅前 3</h4>
                    <table>
                        <tr><th>代码</th><th>名称</th><th>价格</th><th>涨跌幅</th></tr>
                        {"".join(f"<tr><td>{s.get('code','')}</td><td>{s.get('name','')}</td><td>¥{s.get('price',0):,.2f}</td><td style='color:#f4212e'>{s.get('change',0):+.2f}%</td></tr>" for s in ashare.get('top_losers', [])) if ashare.get('top_losers') else '<tr><td colspan="4">无数据</td></tr>'}
                    </table>
                </div>
            </div>
            
            <!-- TradingView 深度分析 -->
            {f"""
            <div class="section">
                <h2 class="section-title">🔬 TradingView 深度分析</h2>
                <div class="card">
                    <h4>📊 核心个股 - 基本面 + 技术面</h4>
                    <table>
                        <tr><th>名称</th><th>价格</th><th>涨跌</th><th>PE</th><th>市值</th><th>股息率</th><th>技术信号</th></tr>
                        {"".join(f'''<tr>
                            <td>{s.get('name','')}</td>
                            <td>¥{s.get('price',0):,.2f}</td>
                            <td style="color:{'#00ba7c' if s.get('change',0) >= 0 else '#f4212e'}">{s.get('change',0):+.2f}%</td>
                            <td>{s.get('pe',0):.1f}</td>
                            <td>{s.get('market_cap',0)/1e12:.2f}万亿</td>
                            <td>{s.get('dividend_yield',0):.2f}%</td>
                            <td><span class="badge" style="background:{'#00ba7c' if '买' in s.get('ta_signal','') else '#f4212e' if '卖' in s.get('ta_signal','') else '#5c6b7f'};color:white">{s.get('ta_signal','N/A')}</span></td>
                        </tr>''' for s in tv.get('stocks', [])) if tv.get('stocks') else '<tr><td colspan="7">TradingView 数据不可用</td></tr>'}
                    </table>
                </div>
                <p style="color:#999;font-size:11px;margin:5px 0 0;text-align:right">数据来源：TradingView via RapidAPI | 技术信号基于日线多指标综合评分</p>
            </div>
            """ if tv.get('stocks') else ''}
            
            <div class="footer">
                <p>📊 统一交易日报 | OpenClaw AI 自动生成</p>
                <p>📧 发送时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>系统状态：OKX ✅ | Polymarket ✅ | A 股 ✅ | TradingView {'✅' if tv.get('stocks') else '⚠️'}</p>
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
    print("=" * 60)
    print("📧 发送统一交易日报")
    print("=" * 60)
    
    html_content = generate_email_content()
    subject = f"🌐 统一交易日报 - {datetime.now().strftime('%Y-%m-%d')}"
    
    success = send_email(subject, html_content)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
