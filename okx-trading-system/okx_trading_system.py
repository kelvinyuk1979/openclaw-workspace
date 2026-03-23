#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📈 OKX 量化自动交易系统
多策略投票 + 自动仓位管理 + 止损止盈（模拟交易）
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
import numpy as np

try:
    import pandas as pd
except ImportError:
    pd = None

# 导入 OKX 客户端
sys.path.insert(0, str(Path(__file__).parent))
from okx_client import OKXClient

# 配置
CONFIG = {
    "initial_capital": 10000.0,  # 初始资金 $10,000 USDT
    "max_position_pct": 0.10,    # 单笔最大仓位 10%
    "stop_loss": -0.05,          # 止损 -5%
    "take_profit": 0.10,         # 止盈 +10%
    "max_positions": 4,          # 最多持仓 4 个币种
    "symbols": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT"],
    "check_interval_minutes": 5,
}

# 数据文件路径
DATA_DIR = Path(__file__).parent / "data"
ACCOUNT_FILE = DATA_DIR / "account.json"
POSITIONS_FILE = DATA_DIR / "positions.json"
TRADES_FILE = DATA_DIR / "trades.json"
SIGNALS_FILE = Path(__file__).parent / "logs" / "latest_signals.json"


class OKXTradingSystem:
    def __init__(self):
        self.client = OKXClient()
        self.ensure_data_dir()
        self.account = self.load_account()
        self.positions = self.load_positions()
        self.trades = self.load_trades()
    
    def ensure_data_dir(self):
        DATA_DIR.mkdir(exist_ok=True)
    
    def load_account(self):
        if ACCOUNT_FILE.exists():
            with open(ACCOUNT_FILE, 'r') as f:
                return json.load(f)
        return {
            "initial_capital": CONFIG["initial_capital"],
            "balance": CONFIG["initial_capital"],
            "total_pnl": 0.0,
            "created_at": datetime.now().isoformat()
        }
    
    def load_positions(self):
        if POSITIONS_FILE.exists():
            with open(POSITIONS_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    def load_trades(self):
        if TRADES_FILE.exists():
            with open(TRADES_FILE, 'r') as f:
                return json.load(f)
        return []
    
    def save_account(self):
        with open(ACCOUNT_FILE, 'w') as f:
            json.dump(self.account, f, indent=2, ensure_ascii=False)
    
    def save_positions(self):
        with open(POSITIONS_FILE, 'w') as f:
            json.dump(self.positions, f, indent=2, ensure_ascii=False)
    
    def save_trades(self):
        with open(TRADES_FILE, 'w') as f:
            json.dump(self.trades, f, indent=2, ensure_ascii=False)
    
    def calculate_rsi(self, prices, period=14):
        """计算 RSI"""
        if len(prices) < period + 1:
            return 50
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices):
        """计算 MACD（不依赖 pandas）"""
        if len(prices) < 26:
            return {'macd': 0, 'signal': 0, 'histogram': 0}
        
        prices = np.array(prices, dtype=float)
        
        # 手动计算 EMA
        def ema(data, span):
            result = np.zeros_like(data, dtype=float)
            multiplier = 2 / (span + 1)
            result[0] = data[0]
            for i in range(1, len(data)):
                result[i] = (data[i] - result[i-1]) * multiplier + result[i-1]
            return result
        
        exp1 = ema(prices, 12)
        exp2 = ema(prices, 26)
        macd = exp1 - exp2
        signal = ema(macd, 9)
        histogram = macd - signal
        
        return {
            'macd': float(macd[-1]),
            'signal': float(signal[-1]),
            'histogram': float(histogram[-1])
        }
    
    def calculate_ma(self, prices, period=20):
        """计算移动平均线"""
        if len(prices) < period:
            return np.mean(prices)
        return np.mean(prices[-period:])
    
    def get_market_data(self, symbol):
        """获取市场数据并计算指标"""
        candles = self.client.get_candles(symbol, bar='15m', limit=100)
        
        if not candles:
            return None
        
        closes = [c['close'] for c in candles]
        current_price = closes[-1]
        
        # 计算技术指标
        rsi = self.calculate_rsi(closes)
        macd_data = self.calculate_macd(closes)
        ma20 = self.calculate_ma(closes, 20)
        ma50 = self.calculate_ma(closes, 50)
        
        return {
            'symbol': symbol,
            'price': current_price,
            'rsi': rsi,
            'macd': macd_data['macd'],
            'macd_signal': macd_data['signal'],
            'macd_hist': macd_data['histogram'],
            'ma20': ma20,
            'ma50': ma50,
            'timestamp': datetime.now().isoformat()
        }
    
    def strategy_momentum(self, data):
        """动量策略"""
        if data['rsi'] < 40:
            return 'LONG', 1
        elif data['rsi'] > 60:
            return 'SHORT', 1
        return 'HOLD', 0
    
    def strategy_mean_reversion(self, data):
        """均值回归策略"""
        if data['rsi'] < 30:
            return 'LONG', 1
        elif data['rsi'] > 70:
            return 'SHORT', 1
        return 'HOLD', 0
    
    def strategy_macd(self, data):
        """MACD 策略"""
        if data['macd'] > data['macd_signal'] and data['macd_hist'] > 0:
            return 'LONG', 1
        elif data['macd'] < data['macd_signal'] and data['macd_hist'] < 0:
            return 'SHORT', 1
        return 'HOLD', 0
    
    def strategy_trend(self, data):
        """趋势跟随策略"""
        if data['price'] > data['ma20'] and data['ma20'] > data['ma50']:
            return 'LONG', 1
        elif data['price'] < data['ma20'] and data['ma20'] < data['ma50']:
            return 'SHORT', 1
        return 'HOLD', 0
    
    def generate_signal(self, symbol):
        """生成交易信号（4 策略投票）"""
        data = self.get_market_data(symbol)
        if not data:
            return None
        
        strategies = [
            ('动量', self.strategy_momentum(data)),
            ('均值回归', self.strategy_mean_reversion(data)),
            ('MACD', self.strategy_macd(data)),
            ('趋势', self.strategy_trend(data))
        ]
        
        long_votes = sum(1 for _, (side, _) in strategies if side == 'LONG')
        short_votes = sum(1 for _, (side, _) in strategies if side == 'SHORT')
        
        if long_votes >= 3:
            signal = 'LONG'
            confidence = long_votes / 4
        elif short_votes >= 3:
            signal = 'SHORT'
            confidence = short_votes / 4
        else:
            signal = 'HOLD'
            confidence = 0
        
        result = {
            'symbol': symbol,
            'price': data['price'],
            'signal': signal,
            'confidence': confidence,
            'votes': {
                'long': long_votes,
                'short': short_votes,
                'hold': 4 - long_votes - short_votes
            },
            'indicators': {
                'rsi': round(data['rsi'], 2),
                'macd': round(data['macd'], 4),
                'ma20': round(data['ma20'], 2),
                'ma50': round(data['ma50'], 2)
            },
            'strategies': [(name, side) for name, (side, _) in strategies],
            'timestamp': datetime.now().isoformat()
        }
        
        return result
    
    def check_stop_loss_take_profit(self):
        """检查止损止盈"""
        closed_positions = []
        
        for symbol, pos in list(self.positions.items()):
            if pos.get('status') != 'open':
                continue
            
            current_data = self.get_market_data(symbol)
            if not current_data:
                continue
            
            current_price = current_data['price']
            entry_price = pos['entry_price']
            side = pos['side']
            
            # 计算盈亏比例
            if side == 'LONG':
                pnl_pct = (current_price - entry_price) / entry_price
            else:
                pnl_pct = (entry_price - current_price) / entry_price
            
            pos['current_pnl_pct'] = pnl_pct
            pos['current_price'] = current_price
            
            # 检查止损止盈
            if pnl_pct <= CONFIG['stop_loss'] or pnl_pct >= CONFIG['take_profit']:
                action = '止损' if pnl_pct <= CONFIG['stop_loss'] else '止盈'
                print(f"🎯 {symbol} {action}: {pnl_pct*100:.2f}%")
                
                # 平仓（模拟）
                close_side = 'SELL' if side == 'LONG' else 'BUY'
                self.client.place_order(symbol, close_side, pos['size'], current_price)
                
                # 记录交易
                trade = {
                    'symbol': symbol,
                    'action': 'CLOSE',
                    'side': close_side,
                    'entry_price': entry_price,
                    'exit_price': current_price,
                    'pnl_pct': pnl_pct,
                    'pnl_usd': pos['size'] * current_price * pnl_pct,
                    'timestamp': datetime.now().isoformat()
                }
                self.trades.append(trade)
                closed_positions.append(symbol)
                
                # 更新账户
                self.account['balance'] += trade['pnl_usd']
                self.account['total_pnl'] += trade['pnl_usd']
                
                # 移除持仓
                del self.positions[symbol]
        
        if closed_positions:
            self.save_account()
            self.save_positions()
            self.save_trades()
        
        return closed_positions
    
    def execute_signal(self, signal):
        """执行交易信号"""
        if signal['signal'] == 'HOLD':
            return
        
        if len(self.positions) >= CONFIG['max_positions']:
            print(f"⚠️ 已达最大持仓数 ({CONFIG['max_positions']})")
            return
        
        symbol = signal['symbol']
        if symbol in self.positions:
            return  # 已有持仓
        
        # 计算仓位大小
        position_value = self.account['balance'] * CONFIG['max_position_pct']
        size = position_value / signal['price']
        
        # 开仓
        side = signal['signal']
        order_side = 'BUY' if side == 'LONG' else 'SELL'
        
        self.client.place_order(symbol, order_side, size, signal['price'])
        
        # 记录持仓
        self.positions[symbol] = {
            'symbol': symbol,
            'side': side,
            'entry_price': signal['price'],
            'size': size,
            'entry_time': datetime.now().isoformat(),
            'status': 'open',
            'current_pnl_pct': 0
        }
        
        # 记录交易
        trade = {
            'symbol': symbol,
            'action': 'OPEN',
            'side': order_side,
            'price': signal['price'],
            'size': size,
            'timestamp': datetime.now().isoformat()
        }
        self.trades.append(trade)
        
        self.save_positions()
        self.save_trades()
        
        print(f"✅ {symbol} {side} @ ${signal['price']:.2f}")
    
    def run_once(self):
        """运行一次检查"""
        print(f"\n{'='*60}")
        print(f"📈 OKX 量化交易系统 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # 检查止损止盈
        print("\n🔍 检查现有持仓...")
        closed = self.check_stop_loss_take_profit()
        if not closed:
            print("  无持仓触及止损/止盈")
        
        # 生成新信号
        print("\n📊 生成交易信号...")
        signals = []
        for symbol in CONFIG['symbols']:
            signal = self.generate_signal(symbol)
            if signal:
                signals.append(signal)
                vote_str = f"L:{signal['votes']['long']} S:{signal['votes']['short']} H:{signal['votes']['hold']}"
                print(f"  {symbol}: {signal['signal']} ({vote_str}) RSI:{signal['indicators']['rsi']:.1f}")
        
        # 保存信号
        with open(SIGNALS_FILE, 'w') as f:
            json.dump({
                'signals': signals,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        # 执行信号
        print("\n⚡ 执行交易...")
        for signal in signals:
            if signal['signal'] != 'HOLD':
                self.execute_signal(signal)
        
        # 显示状态
        print(f"\n💰 账户状态:")
        print(f"  余额：${self.account['balance']:.2f}")
        print(f"  总盈亏：${self.account['total_pnl']:.2f} ({self.account['total_pnl']/self.account['initial_capital']*100:.2f}%)")
        
        if self.positions:
            print(f"\n📦 当前持仓:")
            for sym, pos in self.positions.items():
                pnl = pos.get('current_pnl_pct', 0) * 100
                print(f"  {sym} {pos['side']} @ ${pos['entry_price']:.2f} ({pnl:+.2f}%)")
        
        print(f"\n{'='*60}")
    
    def status(self):
        """显示系统状态"""
        print(f"\n📈 OKX 量化交易系统状态")
        print(f"{'='*60}")
        print(f"账户余额：${self.account['balance']:.2f}")
        print(f"初始资金：${self.account['initial_capital']:.2f}")
        print(f"总收益：${self.account['total_pnl']:.2f} ({self.account['total_pnl']/self.account['initial_capital']*100:.2f}%)")
        
        if self.positions:
            print(f"\n当前持仓:")
            for sym, pos in self.positions.items():
                pnl = pos.get('current_pnl_pct', 0) * 100
                print(f"  - {sym}: {pos['side']} @ ${pos['entry_price']:.2f} (当前：${pos.get('current_price', 0):.2f}, {pnl:+.2f}%)")
        else:
            print(f"\n当前无持仓")
        
        if self.trades:
            print(f"\n最近交易:")
            for trade in self.trades[-5:]:
                print(f"  - {trade['timestamp'][:16]} {trade['symbol']} {trade['action']} {trade['side']} @ ${trade.get('price', trade.get('entry_price', 0)):.2f}")
        
        print()


def main():
    system = OKXTradingSystem()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'status':
            system.status()
        elif cmd == 'run':
            system.run_once()
        elif cmd == 'reset':
            if input("确认重置账户？(y/n): ") == 'y':
                ACCOUNT_FILE.unlink(missing_ok=True)
                POSITIONS_FILE.unlink(missing_ok=True)
                TRADES_FILE.unlink(missing_ok=True)
                print("✅ 账户已重置")
        else:
            print(f"未知命令：{cmd}")
            print("用法：python3 okx_trading_system.py [status|run|reset]")
    else:
        print("用法：python3 okx_trading_system.py [status|run|reset]")
        print("  status - 查看系统状态")
        print("  run    - 运行一次交易检查")
        print("  reset  - 重置账户")


if __name__ == '__main__':
    main()
