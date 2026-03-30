#!/usr/bin/env python3
"""
OKX 实盘检查 - 完整版
执行时间：2026-03-30 21:29
"""

import json
import sys
import requests
from datetime import datetime
from pathlib import Path

# 配置
CONFIG_PATH = Path('/Users/kelvin/.openclaw/workspace/skills/stock-market-pro/quant-trading-system/okx_config.json')
MEMORY_PATH = Path('/Users/kelvin/.openclaw/workspace/memory/2026-03-30.md')

# 加载配置
with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)

okx_cfg = config['okx']
trading_cfg = config['trading']

API_KEY = okx_cfg['api_key']
SECRET_KEY = okx_cfg['secret_key']
PASSPHRASE = okx_cfg['passphrase']

import hmac
import base64
import hashlib

def get_timestamp():
    return datetime.utcnow().isoformat(timespec='milliseconds').split('.')[0] + 'Z'

def sign(timestamp, method, path, body=""):
    message = timestamp + method + path + body
    mac = hmac.new(bytes(SECRET_KEY, 'utf8'), bytes(message, 'utf8'), hashlib.sha256)
    return base64.b64encode(mac.digest()).decode()

def okx_request(method, path, params=None):
    url = f"https://www.okx.com{path}"
    timestamp = get_timestamp()
    body = json.dumps(params) if params else ""
    
    headers = {
        'OK-ACCESS-KEY': API_KEY,
        'OK-ACCESS-SIGN': sign(timestamp, method, path, body),
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': PASSPHRASE,
        'Content-Type': 'application/json'
    }
    
    try:
        if method == 'GET':
            resp = requests.get(url, headers=headers, params=params, timeout=15)
        else:
            resp = requests.post(url, headers=headers, json=params, timeout=15)
        
        result = resp.json()
        if result.get('code') != '0':
            return {'error': result.get('msg', 'Unknown error')}
        return result.get('data', [])
    except Exception as e:
        return {'error': str(e)}

def get_balance():
    data = okx_request('GET', '/api/v5/account/balance')
    if isinstance(data, list) and len(data) > 0:
        total_eq = float(data[0].get('totalEq', 0) or 0)
        usdt_avail = 0
        for detail in data[0].get('details', []):
            if detail.get('ccy') == 'USDT':
                usdt_avail = float(detail.get('availBal', 0) or 0)
        return {'total_eq': total_eq, 'usdt_avail': usdt_avail}
    return {'total_eq': 0, 'usdt_avail': 0}

def get_positions():
    data = okx_request('GET', '/api/v5/account/positions')
    positions = {}
    if isinstance(data, list):
        for pos in data:
            inst_id = pos.get('instId', '')
            if 'USDT' in inst_id:
                symbol = inst_id.replace('-USDT-SWAP', '').replace('-USDT', '')
                pos_side = 'LONG' if pos.get('posSide') == 'long' else 'SHORT'
                avg_px = float(pos.get('avgPx', 0) or 0)
                last_px = float(pos.get('last', 0) or 0)
                upl_ratio = float(pos.get('uplRatio', 0) or 0)
                pos_size = float(pos.get('pos', 0) or 0)
                if pos_size > 0:
                    positions[symbol] = {
                        'side': pos_side,
                        'entry_price': avg_px,
                        'current_price': last_px,
                        'pnl_pct': upl_ratio,
                        'size': pos_size
                    }
    return positions

def get_ticker(symbol):
    inst_id = f"{symbol}-USDT"
    data = okx_request('GET', '/api/v5/market/ticker', {'instId': inst_id})
    if isinstance(data, list) and len(data) > 0:
        return float(data[0].get('last', 0) or 0)
    return None

def get_klines(symbol, limit=50):
    inst_id = f"{symbol}-USDT"
    data = okx_request('GET', '/api/v5/market/candles', {'instId': inst_id, 'bar': '15m', 'limit': limit})
    if isinstance(data, list):
        closes = []
        for k in data:
            try:
                closes.append(float(k[4]))
            except:
                pass
        return closes
    return []

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_macd(prices):
    if len(prices) < 26:
        return 0, 0, 0
    
    def ema(data, span):
        result = [data[0]]
        multiplier = 2 / (span + 1)
        for i in range(1, len(data)):
            result.append((data[i] - result[-1]) * multiplier + result[-1])
        return result
    
    ema12 = ema(prices, 12)
    ema26 = ema(prices, 26)
    macd_line = [ema12[i] - ema26[i] for i in range(len(ema12))]
    signal_line = ema(macd_line, 9)
    histogram = macd_line[-1] - signal_line[-1]
    
    return macd_line[-1], signal_line[-1], histogram

def calculate_ma(prices, period):
    if len(prices) < period:
        return sum(prices) / len(prices)
    return sum(prices[-period:]) / period

def generate_signal(symbol, price, rsi, macd, macd_signal, ma20, ma50):
    votes = {'LONG': 0, 'SHORT': 0, 'HOLD': 0}
    strategies = []
    
    # 策略 1: 动量
    if rsi < 40:
        votes['LONG'] += 1
        strategies.append(('动量', 'LONG'))
    elif rsi > 60:
        votes['SHORT'] += 1
        strategies.append(('动量', 'SHORT'))
    else:
        strategies.append(('动量', 'HOLD'))
    
    # 策略 2: 均值回归
    if rsi < 30:
        votes['LONG'] += 1
        strategies.append(('均值回归', 'LONG'))
    elif rsi > 70:
        votes['SHORT'] += 1
        strategies.append(('均值回归', 'SHORT'))
    else:
        strategies.append(('均值回归', 'HOLD'))
    
    # 策略 3: MACD
    if macd > macd_signal:
        votes['LONG'] += 1
        strategies.append(('MACD', 'LONG'))
    else:
        votes['SHORT'] += 1
        strategies.append(('MACD', 'SHORT'))
    
    # 策略 4: 趋势
    if price > ma20 and ma20 > ma50:
        votes['LONG'] += 1
        strategies.append(('趋势', 'LONG'))
    elif price < ma20 and ma20 < ma50:
        votes['SHORT'] += 1
        strategies.append(('趋势', 'SHORT'))
    else:
        strategies.append(('趋势', 'HOLD'))
    
    if votes['LONG'] >= 3:
        return 'LONG', votes['LONG'] / 4, strategies
    elif votes['SHORT'] >= 3:
        return 'SHORT', votes['SHORT'] / 4, strategies
    else:
        return 'HOLD', 0, strategies

def main():
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S GMT+8')
    result = []
    result.append(f"\n### OKX 实盘检查 ({timestamp})")
    
    print(f"=== OKX 量化实盘检查 ({timestamp}) ===\n")
    
    # 1. API 连接检查
    print("1️⃣ API 连接检查...")
    balance = get_balance()
    if balance['total_eq'] > 0:
        print(f"   ✅ OKX API 连接正常")
        print(f"   总权益：{balance['total_eq']:.2f} USDT")
        print(f"   可用 USDT: {balance['usdt_avail']:.2f} USDT")
        result.append(f"- 总权益：{balance['total_eq']:.2f} USDT")
        result.append(f"- 可用余额：{balance['usdt_avail']:.2f} USDT")
    else:
        print(f"   ❌ API 连接异常")
        result.append(f"- API 连接异常")
    
    # 2. 持仓状态
    print("\n2️⃣ 持仓状态...")
    positions = get_positions()
    print(f"   持仓数：{len(positions)}")
    result.append(f"- 持仓数：{len(positions)}")
    
    for symbol, pos in positions.items():
        pnl_pct = pos['pnl_pct'] * 100
        print(f"   - {symbol}: {pos['side']} @ ${pos['entry_price']:.2f}, 当前 ${pos['current_price']:.2f} ({pnl_pct:+.2f}%)")
        result.append(f"   - {symbol}: {pos['side']} @ ${pos['entry_price']:.2f} ({pnl_pct:+.2f}%)")
    
    # 3. 获取行情和信号
    print("\n3️⃣ 交易信号 (4 策略投票)...")
    signals = {}
    signal_results = []
    
    for symbol in ['BTC', 'ETH']:
        price = get_ticker(symbol)
        if not price:
            print(f"   ⚠️ {symbol}: 获取价格失败")
            continue
        
        klines = get_klines(symbol)
        if len(klines) < 50:
            print(f"   ⚠️ {symbol}: K 线数据不足")
            continue
        
        rsi = calculate_rsi(klines)
        macd, macd_signal, macd_hist = calculate_macd(klines)
        ma20 = calculate_ma(klines, 20)
        ma50 = calculate_ma(klines, 50)
        
        action, confidence, strategies = generate_signal(symbol, price, rsi, macd, macd_signal, ma20, ma50)
        
        signals[symbol] = {
            'price': price,
            'rsi': rsi,
            'action': action,
            'confidence': confidence,
            'strategies': strategies
        }
        
        vote_str = f"L:{sum(1 for _, s in strategies if s=='LONG')} S:{sum(1 for _, s in strategies if s=='SHORT')} H:{sum(1 for _, s in strategies if s=='HOLD')}"
        print(f"   - {symbol}: ${price:.2f}, RSI {rsi:.1f} → {action} ({confidence:.0%}) [{vote_str}]")
        signal_results.append(f"   - {symbol}: ${price:.2f}, RSI {rsi:.1f} → {action} ({confidence:.0%})")
    
    signal_str = ', '.join([f"{k}: {v['action']} ({v['confidence']:.0%})" for k, v in signals.items()])
    result.append(f"- 信号：{signal_str}")
    
    # 4. 止损止盈检查
    print("\n4️⃣ 止损止盈检查 (-5%/+10%)...")
    stop_loss = -0.05
    take_profit = 0.10
    actions_taken = []
    
    for symbol, pos in positions.items():
        pnl_pct = pos['pnl_pct']
        if pnl_pct <= stop_loss:
            print(f"   ⚠️ {symbol} 触及止损：{pnl_pct*100:.2f}% (需平仓)")
            actions_taken.append(f"{symbol} 止损：{pnl_pct*100:.2f}%")
        elif pnl_pct >= take_profit:
            print(f"   🎯 {symbol} 触及止盈：{pnl_pct*100:.2f}% (需平仓)")
            actions_taken.append(f"{symbol} 止盈：{pnl_pct*100:.2f}%")
    
    if not actions_taken:
        print(f"   ✅ 无持仓触及止损/止盈")
        result.append(f"- 止损止盈：无触发")
    else:
        result.append(f"- 止损止盈：{', '.join(actions_taken)}")
    
    # 5. 交易决策
    print("\n5️⃣ 交易决策...")
    max_positions = trading_cfg.get('max_positions', 2)
    
    if len(positions) >= max_positions:
        print(f"   ⚠️ 已达最大持仓数 ({max_positions})，跳过开仓")
        result.append(f"- 决策：已达最大持仓数，保持观望")
    else:
        executed = []
        for symbol, sig in signals.items():
            if sig['action'] in ['LONG', 'SHORT'] and sig['confidence'] >= 0.75:
                if symbol not in positions:
                    if balance['usdt_avail'] > 10:  # 至少有 10 USDT
                        print(f"   🚀 {symbol}: {sig['action']} 信号 (置信度 {sig['confidence']:.0%}) - 建议开仓")
                        executed.append(f"{symbol}: {sig['action']} ({sig['confidence']:.0%})")
                    else:
                        print(f"   ⚠️ {symbol}: {sig['action']} 信号但余额不足")
        
        if not executed:
            print(f"   ⏸️ 无高置信度信号或余额不足，保持观望")
            result.append(f"- 决策：无高置信度信号，保持观望")
        else:
            result.append(f"- 决策：建议开仓 {', '.join(executed)}")
    
    # 6. 写入记忆文件
    print("\n6️⃣ 写入记录...")
    with open(MEMORY_PATH, 'a', encoding='utf-8') as f:
        f.write('\n'.join(result) + '\n')
    print(f"   ✅ 已写入 {MEMORY_PATH}")
    
    print("\n✅ 检查完成")

if __name__ == '__main__':
    main()
