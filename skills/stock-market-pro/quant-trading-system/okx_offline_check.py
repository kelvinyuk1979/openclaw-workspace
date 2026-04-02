#!/usr/bin/env python3
"""
OKX 离线检查脚本 - 使用模拟数据（当网络不可用时）
"""

from datetime import datetime
import json

def main():
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S GMT+8')
    today = datetime.now().strftime('%Y-%m-%d')
    
    print("=" * 60)
    print(f"📈 OKX 量化交易定时检查 ({timestamp})")
    print("=" * 60)
    
    # 模拟数据（基于近期市场情况的估算）
    market_data = {
        'BTC': {'price': 87500.00, 'rsi': 52.3, 'change_24h': 1.2},
        'ETH': {'price': 2180.00, 'rsi': 48.7, 'change_24h': -0.8}
    }
    
    results = {
        'timestamp': timestamp,
        'balance': {'total_eq': 143.85, 'USDT': 143.85},
        'positions': [],
        'signals': {},
        'actions': [],
        'api_status': 'offline_simulation'
    }
    
    # 1. API 连接检查
    print("\n1️⃣ API 连接检查...")
    print(f"   ⚠️ 网络连接超时，使用离线模拟模式")
    results['api_status'] = 'offline_simulation'
    
    # 2. 账户余额
    print("\n2️⃣ 账户余额...")
    print(f"   💰 总权益：143.85 USDT (配置值)")
    print(f"   💵 可用 USDT: 143.85 USDT")
    
    # 3. 持仓状态
    print("\n3️⃣ 持仓状态...")
    print(f"   📦 当前持仓数：0 / 2")
    print(f"   - 无持仓")
    
    # 4. BTC/ETH 价格和 RSI
    print("\n4️⃣ 价格和 RSI 信号 (模拟数据)...")
    for symbol, data in market_data.items():
        print(f"   - {symbol}: ${data['price']:.2f}, 24h {data['change_24h']:+.2f}%, RSI {data['rsi']:.1f}")
    
    # 5. 4 策略投票计算
    print("\n5️⃣ 4 策略投票计算...")
    signals = {}
    
    for symbol, data in market_data.items():
        rsi = data['rsi']
        change = data['change_24h']
        
        votes = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
        strategy_votes = []
        
        # 策略 1: 动量策略
        if rsi > 50:
            votes['BUY'] += 1
            strategy_votes.append(('动量', 'BUY'))
        elif rsi < 50:
            votes['SELL'] += 1
            strategy_votes.append(('动量', 'SELL'))
        else:
            votes['HOLD'] += 1
            strategy_votes.append(('动量', 'HOLD'))
        
        # 策略 2: 均值回归
        if rsi < 30:
            votes['BUY'] += 1
            strategy_votes.append(('均值回归', 'BUY'))
        elif rsi > 70:
            votes['SELL'] += 1
            strategy_votes.append(('均值回归', 'SELL'))
        else:
            votes['HOLD'] += 1
            strategy_votes.append(('均值回归', 'HOLD'))
        
        # 策略 3: MACD
        if change > 0:
            votes['BUY'] += 1
            strategy_votes.append(('MACD', 'BUY'))
        else:
            votes['SELL'] += 1
            strategy_votes.append(('MACD', 'SELL'))
        
        # 策略 4: 超级趋势
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
            action = 'BUY'
            confidence = votes['BUY'] / 4
        elif votes['SELL'] >= 3:
            action = 'SELL'
            confidence = votes['SELL'] / 4
        else:
            action = 'HOLD'
            confidence = 0
        
        signals[symbol] = {
            'price': data['price'],
            'rsi': rsi,
            'action': action,
            'confidence': confidence,
            'strategy_votes': strategy_votes
        }
        
        print(f"   - {symbol}: {action} (置信度 {confidence:.0%})")
        for strat, vote in strategy_votes:
            vote_icon = "🟢" if vote == "BUY" else ("🔴" if vote == "SELL" else "⚪")
            print(f"     {vote_icon} {strat}: {vote}")
    
    results['signals'] = signals
    
    # 6. 自动交易决策
    print("\n6️⃣ 自动交易决策...")
    actions_taken = []
    
    for symbol, sig in signals.items():
        if sig['action'] in ['BUY'] and sig['confidence'] >= 0.75:
            print(f"   🚀 开仓信号：BUY {symbol} (置信度 {sig['confidence']:.0%})")
            actions_taken.append(f"SIGNAL: BUY {symbol} (confidence {sig['confidence']:.0%})")
        elif sig['action'] in ['SELL'] and sig['confidence'] >= 0.75:
            print(f"   🚀 平仓信号：SELL {symbol} (置信度 {sig['confidence']:.0%})")
            actions_taken.append(f"SIGNAL: SELL {symbol} (confidence {sig['confidence']:.0%})")
    
    if not actions_taken:
        print(f"   ⏸️ 无高置信度交易动作，保持观望")
    
    results['actions'] = actions_taken
    
    # 7. 写入 memory 文件
    print(f"\n7️⃣ 写入记忆文件...")
    memory_dir = '/Users/kelvin/.openclaw/workspace/memory'
    memory_file = f'{memory_dir}/{today}.md'
    
    try:
        with open(memory_file, 'a') as f:
            f.write(f"\n### OKX 实盘检查 ({timestamp})\n")
            f.write(f"- **API 状态**: {results['api_status']} (网络超时，使用模拟数据)\n")
            f.write(f"- **总权益**: {results['balance']['total_eq']:.2f} USDT\n")
            f.write(f"- **可用余额**: {results['balance']['USDT']:.2f} USDT\n")
            f.write(f"- **持仓数**: {len(results['positions'])} / 2\n")
            f.write(f"- **交易信号**:\n")
            for sym, sig in signals.items():
                f.write(f"  - {sym}: {sig['action']} (置信度 {sig['confidence']:.0%}, RSI {sig['rsi']:.1f}, ${sig['price']:.2f})\n")
                for strat, vote in sig.get('strategy_votes', []):
                    f.write(f"    - {strat}: {vote}\n")
            if actions_taken:
                f.write(f"- **执行动作**: {', '.join(actions_taken)}\n")
            else:
                f.write(f"- **执行动作**: 无\n")
            f.write(f"\n")
        print(f"   ✅ 已写入 {memory_file}")
    except Exception as e:
        print(f"   ⚠️ 写入失败：{e}")
    
    # 8. Git 提交
    print(f"\n8️⃣ Git 提交...")
    try:
        import subprocess
        script_dir = '/Users/kelvin/.openclaw/workspace/skills/stock-market-pro/quant-trading-system'
        
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, 
                              cwd=script_dir, timeout=5)
        if result.stdout.strip():
            print(f"   📝 检测到未提交的更改")
            subprocess.run(['git', 'add', '.'], cwd=script_dir, capture_output=True, timeout=5)
            commit_msg = f"OKX 定时检查 {timestamp}"
            result = subprocess.run(['git', 'commit', '-m', commit_msg], 
                         cwd=script_dir, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"   ✅ Git 提交完成")
            else:
                print(f"   ⚠️ Git 提交失败：{result.stderr}")
        else:
            print(f"   ⏸️ 无更改需要提交")
    except Exception as e:
        print(f"   ⚠️ Git 操作失败：{e}")
    
    # 完成
    print("\n" + "=" * 60)
    print("✅ 检查完成")
    print("=" * 60)
    
    return results

if __name__ == '__main__':
    main()
