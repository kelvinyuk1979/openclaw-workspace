#!/usr/bin/env python3
"""
从 Binance 获取 BTC/ETH 价格和 K 线数据，计算 RSI 和交易信号
"""

import requests
import json
from datetime import datetime

def get_ticker(symbol):
    """获取当前价格"""
    url = f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT'
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        return float(data['price'])
    except Exception as e:
        print(f"获取 {symbol} 价格失败：{e}")
        return None

def get_klines(symbol, interval='15m', limit=50):
    """获取 K 线数据"""
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}USDT&interval={interval}&limit={limit}'
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        klines = []
        for k in data:
            klines.append({
                'time': k[0],
                'open': float(k[1]),
                'high': float(k[2]),
                'low': float(k[3]),
                'close': float(k[4]),
                'volume': float(k[5])
            })
        return klines
    except Exception as e:
        print(f"获取 {symbol} K 线失败：{e}")
        return []

def calculate_rsi(closes, period=14):
    """计算 RSI"""
    if len(closes) < period + 1:
        return 50
    
    gains = []
    losses = []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i-1]
        if diff > 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(diff))
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(closes, fast=12, slow=26, signal=9):
    """计算 MACD"""
    if len(closes) < slow:
        return 0
    
    ema12 = sum(closes[-fast:]) / fast
    ema26 = sum(closes[-slow:]) / slow
    macd = ema12 - ema26
    return macd

def generate_signal(symbol, price, rsi, macd):
    """4 策略投票"""
    votes = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
    
    # 策略 1: 动量
    if rsi > 50:
        votes['BUY'] += 1
    elif rsi < 50:
        votes['SELL'] += 1
    
    # 策略 2: 均值回归
    if rsi < 30:
        votes['BUY'] += 1
    elif rsi > 70:
        votes['SELL'] += 1
    
    # 策略 3: MACD
    if macd > 0:
        votes['BUY'] += 1
    else:
        votes['SELL'] += 1
    
    # 策略 4: 超级趋势
    if rsi > 45:
        votes['BUY'] += 1
    elif rsi < 45:
        votes['SELL'] += 1
    
    # 决策
    if votes['BUY'] >= 3:
        return 'BUY', votes['BUY'] / 4
    elif votes['SELL'] >= 3:
        return 'SELL', votes['SELL'] / 4
    else:
        return 'HOLD', 0

def main():
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S GMT+8')
    today = datetime.now().strftime('%Y-%m-%d')
    
    print(f"=== Binance 市场数据检查 ({timestamp}) ===\n")
    
    results = {}
    
    for symbol in ['BTC', 'ETH']:
        print(f"{symbol}:")
        
        price = get_ticker(symbol)
        if not price:
            print(f"  价格获取失败")
            results[symbol] = {'price': 'N/A', 'rsi': 'N/A', 'action': 'HOLD', 'confidence': 0}
            continue
        
        klines = get_klines(symbol)
        if not klines:
            print(f"  K 线获取失败")
            results[symbol] = {'price': price, 'rsi': 'N/A', 'action': 'HOLD', 'confidence': 0}
            continue
        
        closes = [k['close'] for k in klines]
        rsi = calculate_rsi(closes)
        macd = calculate_macd(closes)
        
        action, confidence = generate_signal(symbol, price, rsi, macd)
        
        print(f"  价格：${price:.2f}")
        print(f"  RSI: {rsi:.1f}")
        print(f"  MACD: {macd:.2f}")
        print(f"  信号：{action} ({confidence:.0%})")
        
        results[symbol] = {
            'price': price,
            'rsi': rsi,
            'macd': macd,
            'action': action,
            'confidence': confidence
        }
    
    # 写入 memory
    memory_file = f'/Users/kelvin/.openclaw/workspace/memory/{today}.md'
    try:
        with open(memory_file, 'a') as f:
            f.write(f"\n### Binance 市场数据 ({timestamp})\n")
            for sym, data in results.items():
                f.write(f"- {sym}: ${data['price']:.2f}, RSI {data['rsi']:.1f} → {data['action']} ({data['confidence']:.0%})\n")
        print(f"\n✅ 已写入 {memory_file}")
    except Exception as e:
        print(f"\n⚠️ 写入失败：{e}")
    
    print("\n✅ 检查完成")

if __name__ == '__main__':
    main()
