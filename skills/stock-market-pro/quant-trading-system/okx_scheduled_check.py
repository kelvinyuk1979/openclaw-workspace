#!/usr/bin/env python3
"""
OKX 量化交易定时检查脚本
执行：API 连接、余额查询、持仓检查、价格/RSI 信号、4 策略投票、自动交易
"""

import json
import sys
import os
from datetime import datetime

# 导入 OKX 客户端
from okx_client import OKXClient

# 加载配置
with open('okx_config.json', 'r') as f:
    config = json.load(f)

okx_cfg = config['okx']
symbols = config.get('trading', {}).get('symbols', ['BTC', 'ETH'])
max_positions = config.get('trading', {}).get('max_positions', 2)
initial_capital = config.get('trading', {}).get('initial_capital', 10000)

# 初始化 OKX 客户端（实盘）
client = OKXClient(
    api_key=okx_cfg['api_key'],
    secret_key=okx_cfg['secret_key'],
    passphrase=okx_cfg['passphrase'],
    testnet=okx_cfg.get('testnet', False)
)

def get_market_data(symbol, retries=3):
    """获取行情数据（价格、RSI、MACD）"""
    for attempt in range(retries):
        try:
            ticker = client.get_ticker(symbol)
            if not ticker:
                return None
            
            klines = client.get_klines(symbol, interval='15m', limit=50)
            if not klines or len(klines) < 14:
                return {'price': ticker['price'], 'rsi': 50, 'macd': 0}
            
            # 计算 RSI (14 周期)
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
            
            # MACD (简化版：EMA12 - EMA26)
            ema12 = sum(closes[-12:]) / 12 if len(closes) >= 12 else closes[-1]
            ema26 = sum(closes[-26:]) / 26 if len(closes) >= 26 else closes[-1]
            macd = ema12 - ema26
            
            return {'price': ticker['price'], 'rsi': rsi, 'macd': macd}
        except Exception as e:
            if attempt < retries - 1:
                continue
            return None
    return None

def generate_signal(symbol, data):
    """4 策略投票系统"""
    rsi = data['rsi']
    macd = data['macd']
    
    votes = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
    strategy_votes = []
    
    # 策略 1: 动量策略 (Momentum)
    if rsi > 50:
        votes['BUY'] += 1
        strategy_votes.append(('动量', 'BUY'))
    elif rsi < 50:
        votes['SELL'] += 1
        strategy_votes.append(('动量', 'SELL'))
    else:
        votes['HOLD'] += 1
        strategy_votes.append(('动量', 'HOLD'))
    
    # 策略 2: 均值回归 (Mean Reversion)
    if rsi < 30:
        votes['BUY'] += 1
        strategy_votes.append(('均值回归', 'BUY'))
    elif rsi > 70:
        votes['SELL'] += 1
        strategy_votes.append(('均值回归', 'SELL'))
    else:
        votes['HOLD'] += 1
        strategy_votes.append(('均值回归', 'HOLD'))
    
    # 策略 3: MACD 交叉
    if macd > 0:
        votes['BUY'] += 1
        strategy_votes.append(('MACD', 'BUY'))
    else:
        votes['SELL'] += 1
        strategy_votes.append(('MACD', 'SELL'))
    
    # 策略 4: 超级趋势 (SuperTrend - 简化版用 RSI 45 作为阈值)
    if rsi > 45:
        votes['BUY'] += 1
        strategy_votes.append(('超级趋势', 'BUY'))
    elif rsi < 45:
        votes['SELL'] += 1
        strategy_votes.append(('超级趋势', 'SELL'))
    else:
        votes['HOLD'] += 1
        strategy_votes.append(('超级趋势', 'HOLD'))
    
    # 决策
    if votes['BUY'] >= 3:
        return 'BUY', votes['BUY'] / 4, strategy_votes
    elif votes['SELL'] >= 3:
        return 'SELL', votes['SELL'] / 4, strategy_votes
    else:
        return 'HOLD', 0, strategy_votes

def main():
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S GMT+8')
    today = datetime.now().strftime('%Y-%m-%d')
    
    print("=" * 60)
    print(f"📈 OKX 量化交易定时检查 ({timestamp})")
    print("=" * 60)
    
    results = {
        'timestamp': timestamp,
        'balance': {'total_eq': 0, 'USDT': 0},
        'positions': [],
        'signals': {},
        'actions': []
    }
    
    # ========== 1. API 连接检查 ==========
    print("\n1️⃣ API 连接检查...")
    try:
        # 测试连接
        test_result = client.test_connection()
        if test_result:
            print(f"   ✅ OKX API 连接正常")
        else:
            print(f"   ⚠️ OKX API 连接测试返回 False")
    except Exception as e:
        print(f"   ❌ API 连接失败：{e}")
        return
    
    # ========== 2. 账户余额查询 ==========
    print("\n2️⃣ 账户余额查询...")
    try:
        balance = client.get_balance()
        results['balance'] = balance
        total_eq = balance.get('total_eq', 0)
        usdt_avail = balance.get('USDT', 0)
        print(f"   💰 总权益：{total_eq:.2f} USDT")
        print(f"   💵 可用 USDT: {usdt_avail:.2f} USDT")
        
        # 计算收益
        pnl = total_eq - initial_capital
        pnl_pct = (pnl / initial_capital) * 100 if initial_capital > 0 else 0
        print(f"   📊 累计收益：{pnl:+.2f} USDT ({pnl_pct:+.2f}%)")
    except Exception as e:
        print(f"   ❌ 获取余额失败：{e}")
        balance = {'total_eq': 0, 'USDT': 0}
    
    # ========== 3. 持仓状态检查 ==========
    print("\n3️⃣ 持仓状态检查...")
    try:
        positions = client.get_spot_positions()
        results['positions'] = list(positions.keys())
        print(f"   📦 当前持仓数：{len(positions)} / {max_positions}")
        if positions:
            for sym, pos in positions.items():
                pnl_pct = pos.get('pnl_pct', 0)
                size = pos.get('size', 0)
                print(f"   - {sym}: {pos.get('side', 'N/A')} {size} (@ {pos.get('current_price', 0):.2f}, {pnl_pct:.2%})")
        else:
            print(f"   - 无持仓")
    except Exception as e:
        print(f"   ⚠️ 获取持仓失败：{e}")
        positions = {}
    
    # ========== 4. BTC/ETH 价格和 RSI 信号 ==========
    print("\n4️⃣ 价格和 RSI 信号...")
    market_data = {}
    for symbol in symbols:
        data = get_market_data(symbol)
        if data:
            market_data[symbol] = data
            print(f"   - {symbol}: ${data['price']:.2f}, RSI {data['rsi']:.1f}, MACD {data['macd']:.2f}")
        else:
            print(f"   - {symbol}: 数据获取失败")
            market_data[symbol] = {'price': 0, 'rsi': 50, 'macd': 0}
    
    # ========== 5. 4 策略投票计算 ==========
    print("\n5️⃣ 4 策略投票计算...")
    signals = {}
    for symbol in symbols:
        if symbol in market_data and market_data[symbol]['price'] > 0:
            action, confidence, strategy_votes = generate_signal(symbol, market_data[symbol])
            signals[symbol] = {
                'price': market_data[symbol]['price'],
                'rsi': market_data[symbol]['rsi'],
                'action': action,
                'confidence': confidence,
                'strategy_votes': strategy_votes
            }
            
            print(f"   - {symbol}: {action} (置信度 {confidence:.0%})")
            for strat, vote in strategy_votes:
                vote_icon = "🟢" if vote == "BUY" else ("🔴" if vote == "SELL" else "⚪")
                print(f"     {vote_icon} {strat}: {vote}")
        else:
            signals[symbol] = {'price': 'N/A', 'rsi': 'N/A', 'action': 'HOLD', 'confidence': 0, 'strategy_votes': []}
            print(f"   - {symbol}: 无数据，HOLD")
    
    results['signals'] = signals
    
    # ========== 6. 自动开仓/平仓（如触发） ==========
    print("\n6️⃣ 自动交易决策...")
    actions_taken = []
    
    # 检查是否需要平仓（止损/止盈）
    for sym, pos in positions.items():
        pnl_pct = pos.get('pnl_pct', 0)
        if pnl_pct <= config.get('trading', {}).get('stop_loss', -0.05):
            print(f"   🛑 止损触发：{sym} ({pnl_pct:.2%}) - 需要平仓")
            actions_taken.append(f"STOP_LOSS: {sym} ({pnl_pct:.2%})")
        elif pnl_pct >= config.get('trading', {}).get('take_profit', 0.10):
            print(f"   🎯 止盈触发：{sym} ({pnl_pct:.2%}) - 需要平仓")
            actions_taken.append(f"TAKE_PROFIT: {sym} ({pnl_pct:.2%})")
    
    # 检查是否需要开仓
    if len(positions) >= max_positions:
        print(f"   ⚠️ 已达最大持仓数 ({max_positions})，跳过开仓")
    else:
        for symbol, sig in signals.items():
            if sig['action'] in ['BUY'] and sig['confidence'] >= 0.75:
                if symbol not in positions:
                    print(f"   🚀 开仓信号：BUY {symbol} (置信度 {sig['confidence']:.0%})")
                    print(f"   ⏸️ 模拟模式：未执行实际下单")
                    actions_taken.append(f"SIGNAL: BUY {symbol} (confidence {sig['confidence']:.0%})")
            elif sig['action'] in ['SELL'] and sig['confidence'] >= 0.75:
                if symbol in positions:
                    print(f"   🚀 平仓信号：SELL {symbol} (置信度 {sig['confidence']:.0%})")
                    print(f"   ⏸️ 模拟模式：未执行实际下单")
                    actions_taken.append(f"SIGNAL: SELL {symbol} (confidence {sig['confidence']:.0%})")
    
    if not actions_taken:
        print(f"   ⏸️ 无交易动作，保持观望")
    
    results['actions'] = actions_taken
    
    # ========== 7. 写入 memory/2026-04-01.md ==========
    print(f"\n7️⃣ 写入记忆文件...")
    memory_dir = '../../../memory'
    os.makedirs(memory_dir, exist_ok=True)
    memory_file = os.path.join(memory_dir, f'{today}.md')
    
    try:
        with open(memory_file, 'a') as f:
            f.write(f"\n### OKX 实盘检查 ({timestamp})\n")
            f.write(f"- **总权益**: {balance.get('total_eq', 0):.2f} USDT\n")
            f.write(f"- **可用余额**: {balance.get('USDT', 0):.2f} USDT\n")
            f.write(f"- **持仓数**: {len(positions)} / {max_positions}\n")
            if positions:
                for sym, pos in positions.items():
                    f.write(f"  - {sym}: {pos.get('side', 'N/A')} ({pos.get('pnl_pct', 0):.2%})\n")
            f.write(f"- **交易信号**:\n")
            for sym, sig in signals.items():
                f.write(f"  - {sym}: {sig['action']} (置信度 {sig['confidence']:.0%}, RSI {sig['rsi']})\n")
            if actions_taken:
                f.write(f"- **执行动作**: {', '.join(actions_taken)}\n")
            f.write(f"\n")
        print(f"   ✅ 已写入 {memory_file}")
    except Exception as e:
        print(f"   ⚠️ 写入失败：{e}")
    
    # ========== 8. Git 提交 ==========
    print(f"\n8️⃣ Git 提交...")
    try:
        import subprocess
        # 检查是否有未提交的更改
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, 
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        if result.stdout.strip():
            print(f"   📝 检测到未提交的更改")
            # 添加更改
            subprocess.run(['git', 'add', '.'], 
                         cwd=os.path.dirname(os.path.abspath(__file__)))
            # 提交
            commit_msg = f"OKX 定时检查 {timestamp}"
            subprocess.run(['git', 'commit', '-m', commit_msg], 
                         cwd=os.path.dirname(os.path.abspath(__file__)))
            print(f"   ✅ Git 提交完成")
        else:
            print(f"   ⏸️ 无更改需要提交")
    except Exception as e:
        print(f"   ⚠️ Git 操作失败：{e}")
    
    # ========== 完成 ==========
    print("\n" + "=" * 60)
    print("✅ 检查完成")
    print("=" * 60)
    
    return results

if __name__ == '__main__':
    main()
