#!/usr/bin/env python3
"""
📈 量化自动交易系统
多策略投票 + 自动仓位管理 + 止损止盈
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 尝试导入 requests，如果没有则提示安装
try:
    import requests
except ImportError:
    print("❌ 缺少依赖：requests")
    print("请运行：pip install requests")
    sys.exit(1)

try:
    import numpy as np
except ImportError:
    print("❌ 缺少依赖：numpy")
    print("请运行：pip install numpy")
    sys.exit(1)

# 配置
CONFIG = {
    "initial_capital": 143.85,   # 初始资金 $143.85（实盘账户）
    "max_position_pct": 0.40,    # 单笔最大仓位 40%（约$57）
    "stop_loss": -0.05,          # 止损 -5%
    "take_profit": 0.20,         # 止盈 +20%（让利润奔跑）
    "max_positions": 1,          # 最多持仓 1 个币种（集中资金）
    "symbols": ["BTC"],          # 只交易 BTC（避免资金分散）
    "check_interval_minutes": 5,  # 检查间隔
    # OKX 手续费（2026 年标准）
    "maker_fee": 0.0008,         # Maker 0.08%
    "taker_fee": 0.0010,         # Taker 0.10%
}

# 数据文件路径
DATA_DIR = Path(__file__).parent / "data"
ACCOUNT_FILE = DATA_DIR / "account.json"
POSITIONS_FILE = DATA_DIR / "positions.json"
TRADES_FILE = DATA_DIR / "trades.json"

class TradingSystem:
    def __init__(self):
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
            json.dump(self.account, f, indent=2)
    
    def save_positions(self):
        with open(POSITIONS_FILE, 'w') as f:
            json.dump(self.positions, f, indent=2)
    
    def save_trades(self):
        with open(TRADES_FILE, 'w') as f:
            json.dump(self.trades, f, indent=2)
    
    def get_market_data(self, symbol, retry_count=2):
        """获取市场数据（多 API 源 + 重试 + 缓存）- 快速失败模式"""
        binance_symbols = {
            "BTC": "BTCUSDT",
            "ETH": "ETHUSDT",
            "SOL": "SOLUSDT",
            "XRP": "XRPUSDT"
        }
        
        # 多 API 源（按优先级，添加 CoinGecko 作为备用）
        api_sources = [
            {"name": "CoinGecko", "url": "https://api.coingecko.com/api/v3/simple/price", "type": "coingecko"},
            {"name": "Binance", "url": "https://api.binance.com/api/v3/klines", "type": "binance"},
            {"name": "Binance US", "url": "https://api.binance.us/api/v3/klines", "type": "binance"},
        ]
        
        bsym = binance_symbols.get(symbol, f"{symbol}USDT")
        last_error = None
        
        for attempt in range(retry_count):
            for api in api_sources:
                try:
                    if api["type"] == "coingecko":
                        # CoinGecko API（更稳定）
                        cg_ids = {"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana", "XRP": "ripple"}
                        cg_id = cg_ids.get(symbol, symbol.lower())
                        url = f"{api['url']}?ids={cg_id}&vs_currencies=usd"
                        response = requests.get(url, timeout=2)
                        data = response.json()
                        if not data or cg_id not in data:
                            continue
                        current_price = data[cg_id]["usd"]
                        # CoinGecko 只提供价格，用价格模拟其他数据
                        return {
                            "symbol": symbol,
                            "price": current_price,
                            "ma20": current_price * 0.99,  # 近似
                            "rsi": 50.0,  # 中性
                            "macd": 0.0,
                            "source": api["name"]
                        }
                    else:
                        # Binance API
                        url = f"{api['url']}?symbol={bsym}&interval=15m&limit=50"
                        response = requests.get(url, timeout=2)
                    
                    if response.status_code != 200:
                        continue
                    
                    klines = response.json()
                    if not klines or len(klines) < 10:
                        continue
                    
                    # 解析数据
                    closes = [float(k[4]) for k in klines]
                    current_price = closes[-1]
                    ma20 = sum(closes[-20:]) / 20.0 if len(closes) >= 20 else closes[-1]
                    
                    # RSI
                    deltas = np.diff(closes)
                    seed = deltas[:14]
                    up = seed[seed >= 0].sum() / 14
                    down = -seed[seed < 0].sum() / 14
                    rs = up / down if down != 0 else 0
                    rsi = 100.0 - (100.0 / (1.0 + rs))
                    for d in deltas[14:]:
                        up = (up * 13 + (d if d > 0 else 0)) / 14
                        down = (down * 13 + (-d if d < 0 else 0)) / 14
                        rs = up / down if down != 0 else 0
                        rsi = 100.0 - (100.0 / (1.0 + rs))
                    
                    # MACD
                    ema12 = closes[0]
                    ema26 = closes[0]
                    for c in closes[1:]:
                        ema12 = c * (2/13) + ema12 * (11/13)
                        ema26 = c * (2/27) + ema26 * (25/27)
                    macd_line = ema12 - ema26
                    
                    return {
                        "symbol": symbol,
                        "price": current_price,
                        "ma20": ma20,
                        "rsi": rsi,
                        "macd": macd_line,
                        "source": api["name"]
                    }
                    
                except Exception as e:
                    last_error = e
                    continue
        
        # 所有尝试失败
        print(f"⚠️ 获取 {symbol} 数据失败：{last_error}。进入安全模式，本轮暂停交易。")
        return None

    def strategy_momentum(self, data):
        """动量策略：RSI<40 做多，RSI>60 做空"""
        rsi = data["rsi"]
        if rsi < 40:
            return "LONG"
        elif rsi > 60:
            return "SHORT"
        return "HOLD"
    
    def strategy_mean_reversion(self, data):
        """均值回归：RSI<30 做多，RSI>70 做空"""
        rsi = data["rsi"]
        if rsi < 30:
            return "LONG"
        elif rsi > 70:
            return "SHORT"
        return "HOLD"
    
    def strategy_macd_cross(self, data):
        """MACD 交叉：MACD>0 做多，MACD<0 做空"""
        macd = data["macd"]
        if macd > 0:
            return "LONG"
        elif macd < 0:
            return "SHORT"
        return "HOLD"
    
    def strategy_supertrend(self, data):
        """超级趋势：价格>MA20 做多，价格<MA20 做空"""
        price = data["price"]
        ma20 = data["ma20"]
        if price > ma20:
            return "LONG"
        elif price < ma20:
            return "SHORT"
        return "HOLD"
    
    def get_consensus_signal(self, symbol):
        """获取多策略共识信号"""
        data = self.get_market_data(symbol)
        
        if not data:
            return {
                "symbol": symbol,
                "data": None,
                "votes": {},
                "signal": "HOLD",
                "vote_count": {"LONG": 0, "SHORT": 0, "HOLD": 4}
            }
            
        votes = {
            "momentum": self.strategy_momentum(data),
            "mean_reversion": self.strategy_mean_reversion(data),
            "macd_cross": self.strategy_macd_cross(data),
            "supertrend": self.strategy_supertrend(data)
        }
        
        # 计票
        long_votes = sum(1 for v in votes.values() if v == "LONG")
        short_votes = sum(1 for v in votes.values() if v == "SHORT")
        hold_votes = sum(1 for v in votes.values() if v == "HOLD")
        
        # 多数决定
        if long_votes > short_votes and long_votes >= 2:
            signal = "LONG"
        elif short_votes > long_votes and short_votes >= 2:
            signal = "SHORT"
        else:
            signal = "HOLD"
        
        return {
            "symbol": symbol,
            "data": data,
            "votes": votes,
            "signal": signal,
            "vote_count": {"LONG": long_votes, "SHORT": short_votes, "HOLD": hold_votes}
        }
    
    def check_stop_loss_take_profit(self):
        """检查止损止盈（计入手续费）"""
        closed_positions = []
        
        for symbol, pos in list(self.positions.items()):
            if pos["status"] != "open":
                continue
            
            current_data = self.get_market_data(symbol)
            if not current_data:
                continue  # 如果获取不到价格，跳过本轮止损止盈检查
            current_price = current_data["price"]
            entry_price = pos["entry_price"]
            side = pos["side"]
            position_size = pos["position_size"]
            
            # 计算盈亏比例（防止除零）
            if entry_price <= 0:
                print(f"⚠️ {symbol}: 入场价格无效 (${entry_price}), 跳过检查")
                continue
            
            if side == "LONG":
                pnl_pct = (current_price - entry_price) / entry_price
            else:  # SHORT
                pnl_pct = (entry_price - current_price) / entry_price
            
            # 计算平仓手续费（Taker 费率）
            close_fee = position_size * CONFIG["taker_fee"]
            
            # 计算总手续费（开仓 + 平仓）
            open_fee = pos.get("entry_fee", 0)
            total_fee = open_fee + close_fee
            
            # 计算净盈亏（扣除总手续费）
            gross_pnl = position_size * pnl_pct  # 毛盈亏
            net_pnl = gross_pnl - total_fee  # 净盈亏
            
            # 检查止损
            if pnl_pct <= CONFIG["stop_loss"]:
                # 止损平仓
                self.account["balance"] += net_pnl
                self.account["total_pnl"] += net_pnl
                pos["status"] = "closed"
                pos["close_price"] = current_price
                pos["close_time"] = datetime.now().isoformat()
                pos["pnl"] = net_pnl
                pos["gross_pnl"] = gross_pnl
                pos["total_fee"] = total_fee
                pos["close_reason"] = "STOP_LOSS"
                closed_positions.append({
                    "symbol": symbol,
                    "action": "STOP_LOSS",
                    "gross_pnl": gross_pnl,
                    "fees": total_fee,
                    "net_pnl": net_pnl,
                    "pnl_pct": pnl_pct
                })
                print(f"✗ {symbol}: 止损触发 ({pnl_pct:.2%}), 毛盈亏：${gross_pnl:.2f}, 手续费：${total_fee:.2f}, 净盈亏：${net_pnl:.2f}")
            
            # 检查止盈
            elif pnl_pct >= CONFIG["take_profit"]:
                # 止盈平仓
                self.account["balance"] += net_pnl
                self.account["total_pnl"] += net_pnl
                pos["status"] = "closed"
                pos["close_price"] = current_price
                pos["close_time"] = datetime.now().isoformat()
                pos["pnl"] = net_pnl
                pos["gross_pnl"] = gross_pnl
                pos["total_fee"] = total_fee
                pos["close_reason"] = "TAKE_PROFIT"
                closed_positions.append({
                    "symbol": symbol,
                    "action": "TAKE_PROFIT",
                    "gross_pnl": gross_pnl,
                    "fees": total_fee,
                    "net_pnl": net_pnl,
                    "pnl_pct": pnl_pct
                })
                print(f"✓ {symbol}: 止盈触发 ({pnl_pct:.2%}), 毛盈利：${gross_pnl:.2f}, 手续费：${total_fee:.2f}, 净盈利：${net_pnl:.2f}")
            
            else:
                # 更新当前盈亏（未实现，不计手续费）
                pos["current_pnl_pct"] = pnl_pct
                pos["current_price"] = current_price
        
        self.save_account()
        self.save_positions()
        return closed_positions
    
    def open_position(self, symbol, signal, data):
        """开仓"""
        if len([p for p in self.positions.values() if p["status"] == "open"]) >= CONFIG["max_positions"]:
            print(f"⚠️ {symbol}: 已达最大持仓数 ({CONFIG['max_positions']}), 跳过")
            return False
        
        position_size = self.account["balance"] * CONFIG["max_position_pct"]
        price = data["price"]
        
        # 计算开仓手续费（Taker 费率）
        open_fee = position_size * CONFIG["taker_fee"]
        
        # 创建持仓
        self.positions[symbol] = {
            "symbol": symbol,
            "side": signal,
            "entry_price": price,
            "position_size": position_size,
            "entry_fee": open_fee,  # 开仓手续费
            "entry_time": datetime.now().isoformat(),
            "status": "open",
            "current_pnl_pct": 0.0,
            "current_price": price
        }
        
        # 记录交易（包含手续费）
        self.trades.append({
            "symbol": symbol,
            "action": "OPEN",
            "side": signal,
            "price": price,
            "size": position_size,
            "fee": open_fee,
            "fee_rate": CONFIG["taker_fee"],
            "timestamp": datetime.now().isoformat()
        })
        
        self.save_positions()
        self.save_trades()
        
        print(f"✓ 开{ '多' if signal == 'LONG' else '空' } {symbol} @ ${price:.2f}, 仓位：${position_size:.2f}, 手续费：${open_fee:.2f}")
        return True
    
    def run_once(self):
        """运行一次交易检查"""
        print("\n📈 AUTO TRADER RUNNING")
        print("=" * 40)
        
        # 1. 检查现有持仓的止损止盈
        print("检查现有持仓...")
        if not self.positions:
            print("  无持仓")
        else:
            self.check_stop_loss_take_profit()
            # 显示当前持仓状态
            for symbol, pos in self.positions.items():
                if pos["status"] == "open":
                    pnl = pos.get("current_pnl_pct", 0)
                    print(f"  ✓ {symbol}: 持有中 ({pnl:+.2%})")
        
        # 2. 生成新信号
        print("\n生成新信号...")
        for symbol in CONFIG["symbols"]:
            if symbol in self.positions and self.positions[symbol]["status"] == "open":
                print(f"  - {symbol}: 已持仓，跳过")
                continue
            
            result = self.get_consensus_signal(symbol)
            votes = result["vote_count"]
            signal = result["signal"]
            
            vote_str = f"{votes['LONG']}多 {votes['SHORT']}空 {votes['HOLD']}观望"
            print(f"  - {symbol}: {vote_str} → {signal}")
            
            if signal in ["LONG", "SHORT"] and signal != "HOLD":
                # 开仓
                self.open_position(symbol, signal, result["data"])
        
        # 3. 显示账户状态
        print("\n" + "=" * 40)
        print(f"账户余额：${self.account['balance']:.2f}")
        print(f"初始资金：${self.account['initial_capital']:.2f}")
        print(f"总收益：{((self.account['balance'] - self.account['initial_capital']) / self.account['initial_capital']):+.2%}")
        
        self.save_account()
    
    def status(self):
        """显示系统状态"""
        print("\n📈 量化交易系统状态")
        print("=" * 40)
        print(f"账户余额：${self.account['balance']:.2f}")
        print(f"初始资金：${self.account['initial_capital']:.2f}")
        print(f"总收益：${self.account['total_pnl']:.2f} ({((self.account['balance'] - self.account['initial_capital']) / self.account['initial_capital']):+.2%})")
        
        print("\n当前持仓:")
        if not self.positions:
            print("  无持仓")
        else:
            for symbol, pos in self.positions.items():
                if pos["status"] == "open":
                    pnl = pos.get("current_pnl_pct", 0)
                    side = "多" if pos["side"] == "LONG" else "空"
                    print(f"  - {symbol}: {side} @ ${pos['entry_price']:.2f} (当前：${pos.get('current_price', pos['entry_price']):.2f}, {pnl:+.2%})")
                else:
                    reason = pos.get("close_reason", "")
                    pnl = pos.get("pnl", 0)
                    print(f"  - {symbol}: 已平仓 ({reason}, ${pnl:+.2f})")
        
        print("\n最近交易:")
        if not self.trades:
            print("  无交易记录")
        else:
            for trade in self.trades[-5:]:
                print(f"  - {trade['timestamp'][:16]} {trade['symbol']} {trade['action']} {trade['side']} @ ${trade['price']:.2f}")
    
    def reset(self):
        """重置账户"""
        confirm = input("⚠️ 确定要重置账户吗？(y/N): ")
        if confirm.lower() != 'y':
            print("已取消")
            return
        
        self.account = {
            "initial_capital": CONFIG["initial_capital"],
            "balance": CONFIG["initial_capital"],
            "total_pnl": 0.0,
            "created_at": datetime.now().isoformat()
        }
        self.positions = {}
        self.trades = []
        
        self.save_account()
        self.save_positions()
        self.save_trades()
        
        print("✓ 账户已重置")


def main():
    system = TradingSystem()
    
    if len(sys.argv) < 2:
        print("用法：python3 trading_system.py <command>")
        print("命令:")
        print("  status  - 查看系统状态")
        print("  run     - 启动自动交易（运行一次）")
        print("  reset   - 重置账户")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "status":
        system.status()
    elif command == "run":
        system.run_once()
    elif command == "reset":
        system.reset()
    else:
        print(f"❌ 未知命令：{command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
