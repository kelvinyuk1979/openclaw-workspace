#!/usr/bin/env python3
"""
OKX 量化检查脚本 - 实盘模式
每 5 分钟检查一次账户状态和交易信号
"""

import json
import sys
from datetime import datetime
from okx_client import OKXClient

# 加载配置
with open('okx_config.json', 'r') as f:
    config = json.load(f)

okx_cfg = config['okx']
symbols = config.get('symbols', ['BTC', 'ETH'])
max_positions = config.get('max_positions', 2)
position_pct = config.get('position_pct', 0.4)
stop_loss = config.get('stop_loss', -0.05)
take_profit = config.get('take_profit', 0.20)

# 初始化 OKX 客户端（实盘）
client = OKXClient(
    api_key=okx_cfg['api_key'],
    secret_key=okx_cfg['secret_key'],
    passphrase=okx_cfg['passphrase'],
    testnet=okx_cfg.get('testnet', False)
)

def get_market_data(symbol):
    """获取行情数据"""
    ticker = client.get_ticker(symbol)
    if not ticker:
        return None
    
    klines = client.get_klines(symbol, interval='15m', limit=50)
    if not klines:
        return {
            'price': ticker['price'],
            'rsi': 50,
            'macd': 0,
            'signal': 'HOLD'
        }
    
    # 计算 RSI（简化版）
    closes = [k['close'] for k in klines[-14:]]
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
    
    avg_gain = sum(gains) / len(gains) if gains else 0
    avg_loss = sum(losses) / len(losses) if losses else 1
    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    rsi = 100 - (100 / (1 + rs))
    
    # 简单 MACD 判断
    ema12 = sum(closes[-12:]) / 12 if len(closes) >= 12 else closes[-1]
    ema26 = sum(closes[-26:]) / 26 if len(closes) >= 26 else closes[-1]
    macd = ema12 - ema26
    
    return {
        'price': ticker['price'],
        'rsi': rsi,
        'macd': macd,
        'signal': 'HOLD'
    }

def generate_signal(symbol, data):
    """生成交易信号（4 策略投票）"""
    rsi = data['rsi']
    macd = data['macd']
    
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
    
    # 策略 4: 超级趋势（简化为价格趋势）
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
    """主检查流程"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%M GMT+8')
    
    print(f"=== OKX 量化实盘检查 ({timestamp}) ===\n")
    
    # 1. 检查 API 连接
    print("1️⃣ API 连接检查...")
    try:
        balance = client.get_balance()
        print(f"   ✅ OKX API 连接正常")
        print(f"   总权益：{balance['total_eq']:.2f} USDT")
        print(f"   可用：{balance['USDT']:.2f} USDT")
    except Exception as e:
        print(f"   ❌ API 连接失败：{e}")
        return
    
    # 2. 获取持仓
    print("\n2️⃣ 持仓状态...")
    positions = client.get_positions()
    print(f"   持仓数：{len(positions)}")
    for sym, pos in positions.items():
        print(f"   - {sym}: {pos['side']} {pos['pnl_pct']:.2%}")
    
    # 3. 获取行情和信号
    print("\n3️⃣ 交易信号...")
    signals = {}
    for symbol in symbols:
        data = get_market_data(symbol)
        if data:
            action, confidence = generate_signal(symbol, data)
            signals[symbol] = {
                'price': data['price'],
                'rsi': data['rsi'],
                'action': action,
                'confidence': confidence
            }
            print(f"   - {symbol}: ${data['price']:.2f}, RSI {data['rsi']:.1f} → {action} ({confidence:.0%})")
    
    # 4. 系统决策
    print("\n4️⃣ 系统决策...")
    if len(positions) >= max_positions:
        print(f"   ⚠️ 已达最大持仓数 ({max_positions})，跳过开仓")
    else:
        for symbol, sig in signals.items():
            if sig['action'] in ['BUY', 'SELL'] and sig['confidence'] >= 0.75:
                if symbol not in positions:
                    print(f"   🚀 建议：{sig['action']} {symbol} (置信度 {sig['confidence']:.0%})")
                    # TODO: 实盘交易调用
                    # client.open_position(symbol, sig['action'], ...)
        if not any(s['confidence'] >= 0.75 for s in signals.values()):
            print(f"   ⏸️ 无高置信度信号，保持观望")
    
    # 5. 写入记忆文件
    print("\n5️⃣ 记录检查结果...")
    try:
        with open('../../../memory/2026-03-23.md', 'a') as f:
            f.write(f"\n### OKX 实盘检查 ({timestamp})\n")
            f.write(f"- 总权益：{balance['total_eq']:.2f} USDT\n")
            f.write(f"- 持仓数：{len(positions)}\n")
            f.write(f"- 信号：{', '.join([f'{k}: {v[\"action\"]}' for k, v in signals.items()])}\n")
        print(f"   ✅ 已写入 memory/2026-03-23.md")
    except Exception as e:
        print(f"   ⚠️ 写入失败：{e}")
    
    print("\n✅ 检查完成")

if __name__ == '__main__':
    main()
