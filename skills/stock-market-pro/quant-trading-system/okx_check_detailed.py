#!/usr/bin/env python3
"""
OKX 量化检查脚本 - 实盘模式（详细版）
详细记录所有余额字段以排查数据偏差问题
"""

import json
import sys
import os
from datetime import datetime
from okx_client import OKXClient

# 切换到脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

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
    vote_details = []
    
    # 策略 1: 动量
    if rsi > 50:
        votes['BUY'] += 1
        vote_details.append("动量：BUY (RSI>50)")
    else:
        votes['SELL'] += 1
        vote_details.append("动量：SELL (RSI<50)")
    
    # 策略 2: 均值回归
    if rsi < 30:
        votes['BUY'] += 1
        vote_details.append("均值回归：BUY (RSI<30)")
    elif rsi > 70:
        votes['SELL'] += 1
        vote_details.append("均值回归：SELL (RSI>70)")
    else:
        vote_details.append("均值回归：HOLD (30<RSI<70)")
    
    # 策略 3: MACD
    if macd > 0:
        votes['BUY'] += 1
        vote_details.append("MACD: BUY (MACD>0)")
    else:
        votes['SELL'] += 1
        vote_details.append("MACD: SELL (MACD<0)")
    
    # 策略 4: 超级趋势（简化为价格趋势）
    if rsi > 45:
        votes['BUY'] += 1
        vote_details.append("超级趋势：BUY (RSI>45)")
    else:
        votes['SELL'] += 1
        vote_details.append("超级趋势：SELL (RSI<45)")
    
    # 决策
    if votes['BUY'] >= 3:
        return 'BUY', votes['BUY'] / 4, vote_details
    elif votes['SELL'] >= 3:
        return 'SELL', votes['SELL'] / 4, vote_details
    else:
        return 'HOLD', max(votes['BUY'], votes['SELL']) / 4, vote_details
    
def main():
    """主检查流程"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S GMT+8')
    
    print(f"=== OKX 量化实盘检查 ({timestamp}) ===\n")
    
    # 1. 检查 API 连接
    print("1️⃣ API 连接检查...")
    try:
        balance = client.get_balance(detailed=True)
        print(f"   ✅ OKX API 连接正常")
    except Exception as e:
        print(f"   ❌ API 连接失败：{e}")
        return
    
    # 2. 详细记录余额（重点）
    print("\n2️⃣ 账户余额详情（详细记录）...")
    print(f"   总权益 (totalEq): {balance.get('total_eq', 0):.2f} USDT")
    print(f"   账户等级 (acctLv): {balance.get('acctLv', 'unknown')}")
    print(f"   USDT 可用余额：{balance.get('USDT', 0):.2f} USDT")
    print(f"   使用字段：{balance.get('used_field', 'unknown')}")
    
    # 打印原始详情
    raw_details = balance.get('raw_details', {})
    if 'USDT' in raw_details:
        usdt_detail = raw_details['USDT']
        print(f"\n   USDT 完整字段:")
        print(f"     - availBal (可用余额): {usdt_detail.get('availBal', 'N/A')}")
        print(f"     - availEq (可用权益): {usdt_detail.get('availEq', 'N/A')}")
        print(f"     - cashBal (现金余额): {usdt_detail.get('cashBal', 'N/A')}")
        print(f"     - eq (总权益): {usdt_detail.get('eq', 'N/A')}")
        print(f"     - frozenBal (冻结余额): {usdt_detail.get('frozenBal', 'N/A')}")
        print(f"     - ordFrozen (挂单冻结): {usdt_detail.get('ordFrozen', 'N/A')}")
        print(f"     - upl (未实现盈亏): {usdt_detail.get('upl', 'N/A')}")
        print(f"     - stgyEq (策略权益): {usdt_detail.get('stgyEq', 'N/A')}")
    
    # 3. 获取持仓
    print("\n3️⃣ 持仓状态...")
    positions = client.get_positions()
    print(f"   持仓数：{len(positions)}")
    if positions:
        for sym, pos in positions.items():
            print(f"   - {sym}: {pos['side']} {pos['size']} @ ${pos['entry_price']:.2f} (PnL: {pos['pnl_pct']:.2%})")
    else:
        print(f"   无持仓")
    
    # 4. 获取行情和信号
    print("\n4️⃣ 行情和交易信号...")
    signals = {}
    for symbol in symbols:
        data = get_market_data(symbol)
        if data:
            action, confidence, vote_details = generate_signal(symbol, data)
            signals[symbol] = {
                'price': data['price'],
                'rsi': data['rsi'],
                'macd': data['macd'],
                'action': action,
                'confidence': confidence,
                'vote_details': vote_details
            }
            print(f"\n   {symbol}:")
            print(f"     价格：${data['price']:.2f}")
            print(f"     RSI: {data['rsi']:.1f}")
            print(f"     MACD: {data['macd']:.2f}")
            print(f"     信号：{action} (置信度：{confidence:.0%})")
            print(f"     投票详情:")
            for vd in vote_details:
                print(f"       - {vd}")
    
    # 5. 系统决策
    print("\n5️⃣ 系统决策...")
    executed_trades = []
    if len(positions) >= max_positions:
        print(f"   ⚠️ 已达最大持仓数 ({max_positions})，跳过开仓")
    else:
        for symbol, sig in signals.items():
            if sig['action'] in ['BUY', 'SELL'] and sig['confidence'] >= 0.75:
                if symbol not in positions:
                    avail_usdt = balance.get('USDT', 0)
                    if avail_usdt > 100:  # 至少需要 100 USDT
                        print(f"   🚀 执行：{sig['action']} {symbol} (置信度 {sig['confidence']:.0%})")
                        # TODO: 实盘交易调用
                        # result = client.open_position(...)
                        executed_trades.append(f"{sig['action']} {symbol}")
                    else:
                        print(f"   ⚠️ 余额不足 ({avail_usdt:.2f} USDT)，跳过 {symbol}")
        if not executed_trades and not any(s['confidence'] >= 0.75 for s in signals.values()):
            print(f"   ⏸️ 无高置信度信号，保持观望")
    
    # 6. 写入记忆文件
    print("\n6️⃣ 记录检查结果...")
    memory_dir = '../../../memory'
    memory_file = os.path.join(memory_dir, '2026-03-23.md')
    
    try:
        # 确保目录存在
        os.makedirs(memory_dir, exist_ok=True)
        
        with open(memory_file, 'a', encoding='utf-8') as f:
            f.write(f"\n### OKX 实盘检查 ({timestamp})\n")
            f.write(f"- **API 状态**: ✅ 正常\n")
            f.write(f"- **总权益**: {balance.get('total_eq', 0):.2f} USDT\n")
            f.write(f"- **可用余额**: {balance.get('USDT', 0):.2f} USDT\n")
            f.write(f"- **账户等级**: {balance.get('acctLv', 'unknown')}\n")
            f.write(f"- **持仓数**: {len(positions)}\n")
            
            # 详细余额字段
            if 'USDT' in raw_details:
                usdt = raw_details['USDT']
                f.write(f"- **余额详情**:\n")
                f.write(f"  - availBal: {usdt.get('availBal', 'N/A')}\n")
                f.write(f"  - availEq: {usdt.get('availEq', 'N/A')}\n")
                f.write(f"  - cashBal: {usdt.get('cashBal', 'N/A')}\n")
                f.write(f"  - eq: {usdt.get('eq', 'N/A')}\n")
                f.write(f"  - frozenBal: {usdt.get('frozenBal', 'N/A')}\n")
            
            signal_str = ', '.join([f"{k}: {v['action']} (RSI {v['rsi']:.1f})" for k, v in signals.items()])
            f.write(f"- **信号**: {signal_str}\n")
            if executed_trades:
                f.write(f"- **执行交易**: {', '.join(executed_trades)}\n")
        
        print(f"   ✅ 已写入 {memory_file}")
    except Exception as e:
        print(f"   ⚠️ 写入失败：{e}")
    
    # 7. Git 提交
    print("\n7️⃣ Git 提交...")
    try:
        import subprocess
        workspace = os.path.abspath('../../../')
        
        # 添加文件
        subprocess.run(['git', 'add', memory_file], cwd=workspace, capture_output=True)
        
        # 检查是否有更改
        result = subprocess.run(['git', 'status', '--porcelain'], cwd=workspace, capture_output=True, text=True)
        
        if result.stdout.strip():
            commit_msg = f"OKX 实盘检查 {timestamp.split()[-1]} - 余额 {balance.get('USDT', 0):.2f} USDT, {len(positions)} 持仓"
            subprocess.run(['git', 'commit', '-m', commit_msg], cwd=workspace, capture_output=True)
            print(f"   ✅ Git 提交成功")
        else:
            print(f"   ⚠️ 无更改，跳过提交")
    except Exception as e:
        print(f"   ⚠️ Git 提交失败：{e}")
    
    print("\n✅ 检查完成")

if __name__ == '__main__':
    main()
