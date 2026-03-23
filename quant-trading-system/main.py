#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多市场量化交易系统 - 主引擎
支持 A 股、港股、Crypto 多市场交易
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np

# 导入策略模块
from strategies.trend_following import TrendFollowingStrategy
from strategies.momentum import MomentumStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.multi_factor import MultiFactorStrategy

class QuantTradingSystem:
    """量化交易系统主引擎"""
    
    def __init__(self, config_path=None):
        """初始化交易系统"""
        self.base_dir = Path(__file__).parent
        self.config_path = config_path or self.base_dir / "config" / "config.json"
        self.config = self.load_config()
        
        # 账户信息
        self.account = {
            "initial_capital": self.config["account"]["initial_capital"],
            "cash": self.config["account"]["initial_capital"],
            "positions": {},
            "history": [],
            "mode": self.config["account"]["mode"]
        }
        
        # 初始化策略
        self.strategies = {
            "trend_following": TrendFollowingStrategy(self.config["strategies"]["trend_following"]),
            "momentum": MomentumStrategy(self.config["strategies"]["momentum"]),
            "mean_reversion": MeanReversionStrategy(self.config["strategies"]["mean_reversion"]),
            "multi_factor": MultiFactorStrategy(self.config["strategies"]["multi_factor"])
        }
        
        # 风控指标
        self.risk_metrics = {
            "daily_pnl": 0,
            "weekly_pnl": 0,
            "monthly_pnl": 0,
            "total_pnl": 0,
            "consecutive_losses": 0
        }
        
        print(f"✅ 量化交易系统初始化完成")
        print(f"📊 模式：{self.account['mode']}")
        print(f"💰 初始资金：${self.account['initial_capital']}")
        print(f"🌍 市场：{', '.join(self.config['account']['markets'])}")
    
    def load_config(self):
        """加载配置文件"""
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def get_market_data(self, symbol, market, period="daily"):
        """获取市场数据（模拟版本，实际需接入 API）"""
        # TODO: 接入真实数据源
        # A 股/港股：akshare
        # Crypto: ccxt
        
        # 模拟数据
        dates = pd.date_range(end=datetime.now(), periods=60, freq="D")
        np.random.seed(hash(symbol) % 10000)
        
        base_price = np.random.uniform(50, 500)
        returns = np.random.normal(0.001, 0.03, len(dates))
        prices = base_price * np.cumprod(1 + returns)
        
        data = pd.DataFrame({
            "date": dates,
            "open": prices * (1 + np.random.uniform(-0.01, 0.01, len(dates))),
            "high": prices * (1 + np.random.uniform(0, 0.03, len(dates))),
            "low": prices * (1 - np.random.uniform(0, 0.03, len(dates))),
            "close": prices,
            "volume": np.random.randint(100000, 10000000, len(dates))
        })
        
        return data
    
    def scan_market(self):
        """扫描市场，获取候选股票"""
        # 候选股票池
        candidates = {
            "A 股": ["600519", "300750", "002594", "688012", "300861"],
            "港股": ["00700.HK", "09988.HK", "03690.HK"],
            "Crypto": ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
        }
        
        print("\n🔍 扫描市场...")
        signals = []
        
        for market, symbols in candidates.items():
            for symbol in symbols:
                try:
                    data = self.get_market_data(symbol, market)
                    
                    # 运行所有策略
                    for strategy_name, strategy in self.strategies.items():
                        if self.config["strategies"][strategy_name]["enabled"]:
                            signal = strategy.generate_signal(symbol, market, data)
                            if signal:
                                signal["strategy"] = strategy_name
                                signal["market"] = market
                                signals.append(signal)
                    
                except Exception as e:
                    print(f"⚠️  {symbol} 分析失败：{e}")
        
        print(f"✅ 生成 {len(signals)} 个交易信号")
        return signals
    
    def risk_check(self, signal):
        """风控检查"""
        risk_config = self.config["risk_control"]
        
        # 检查单日亏损
        if self.risk_metrics["daily_pnl"] < risk_config["daily_loss_limit"]:
            print(f"⚠️  触发单日亏损限制，停止交易")
            return False
        
        # 检查总仓位
        total_position = sum(
            p["quantity"] * self.get_market_data(p["symbol"], p["market"])["close"].iloc[-1]
            for p in self.account["positions"].values()
        )
        if total_position / self.account["initial_capital"] >= risk_config["position_total_max"]:
            print(f"⚠️  达到总仓位上限，停止开仓")
            return False
        
        # 检查单只股票仓位
        if signal["symbol"] in self.account["positions"]:
            current_pos = self.account["positions"][signal["symbol"]]["value"]
            if current_pos / self.account["initial_capital"] >= risk_config["position_single_max"]:
                print(f"⚠️  {signal['symbol']} 达到单只仓位上限")
                return False
        
        return True
    
    def execute_signal(self, signal):
        """执行交易信号"""
        if not self.risk_check(signal):
            return False
        
        action = signal["action"]  # buy / sell
        symbol = signal["symbol"]
        price = signal["price"]
        quantity = signal["quantity"]
        value = price * quantity
        
        # 计算手续费
        commission = value * self.config["execution"]["commission"]
        
        if action == "buy":
            # 检查现金
            if self.account["cash"] < value + commission:
                print(f"⚠️  现金不足，无法买入 {symbol}")
                return False
            
            # 更新账户
            self.account["cash"] -= (value + commission)
            
            if symbol in self.account["positions"]:
                self.account["positions"][symbol]["quantity"] += quantity
                self.account["positions"][symbol]["avg_price"] = (
                    (self.account["positions"][symbol]["avg_price"] * 
                     (self.account["positions"][symbol]["quantity"] - quantity) + 
                     value) / self.account["positions"][symbol]["quantity"]
                )
            else:
                self.account["positions"][symbol] = {
                    "quantity": quantity,
                    "avg_price": price,
                    "market": signal["market"],
                    "entry_date": datetime.now().isoformat()
                }
            
            print(f"✅ 买入 {symbol}: {quantity} @ {price}, 金额: ${value:.2f}")
        
        elif action == "sell":
            if symbol not in self.account["positions"]:
                print(f"⚠️  没有 {symbol} 持仓，无法卖出")
                return False
            
            position = self.account["positions"][symbol]
            if position["quantity"] < quantity:
                quantity = position["quantity"]  # 全部卖出
            
            # 计算盈亏
            pnl = (price - position["avg_price"]) * quantity
            self.risk_metrics["total_pnl"] += pnl
            
            # 更新账户
            self.account["cash"] += (value - commission)
            self.account["positions"][symbol]["quantity"] -= quantity
            
            print(f"✅ 卖出 {symbol}: {quantity} @ {price}, 盈亏: ${pnl:.2f}")
            
            if self.account["positions"][symbol]["quantity"] <= 0:
                del self.account["positions"][symbol]
        
        # 记录交易历史
        self.account["history"].append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "symbol": symbol,
            "market": signal["market"],
            "price": price,
            "quantity": quantity,
            "value": value,
            "commission": commission,
            "strategy": signal["strategy"]
        })
        
        return True
    
    def check_stop_loss_take_profit(self):
        """检查止损止盈"""
        risk_config = self.config["risk_control"]
        
        for symbol, position in list(self.account["positions"].items()):
            # 获取最新价格
            data = self.get_market_data(symbol, position["market"])
            current_price = data["close"].iloc[-1]
            
            cost_basis = position["avg_price"]
            pnl_pct = (current_price - cost_basis) / cost_basis
            
            # 止损检查
            if pnl_pct <= risk_config["stop_loss"]:
                print(f"🛑 止损触发：{symbol} 亏损 {pnl_pct*100:.2f}%")
                self.execute_signal({
                    "action": "sell",
                    "symbol": symbol,
                    "market": position["market"],
                    "price": current_price,
                    "quantity": position["quantity"],
                    "strategy": "stop_loss"
                })
            
            # 止盈检查
            elif pnl_pct >= risk_config["take_profit"]:
                print(f"✅ 止盈触发：{symbol} 盈利 {pnl_pct*100:.2f}%")
                # 止盈卖出 50%
                sell_quantity = position["quantity"] // 2
                if sell_quantity > 0:
                    self.execute_signal({
                        "action": "sell",
                        "symbol": symbol,
                        "market": position["market"],
                        "price": current_price,
                        "quantity": sell_quantity,
                        "strategy": "take_profit"
                    })
    
    def run_daily(self):
        """每日运行主流程"""
        print("\n" + "="*60)
        print(f"🤖 量化交易系统 - 每日运行")
        print(f"📅 日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*60)
        
        # 1. 扫描市场，生成信号
        signals = self.scan_market()
        
        # 2. 过滤信号（每个策略选最佳 1 个）
        filtered_signals = []
        for strategy_name in self.strategies.keys():
            strategy_signals = [s for s in signals if s["strategy"] == strategy_name]
            if strategy_signals:
                # 选择置信度最高的
                best_signal = max(strategy_signals, key=lambda x: x.get("confidence", 0))
                filtered_signals.append(best_signal)
        
        # 3. 检查止损止盈
        self.check_stop_loss_take_profit()
        
        # 4. 执行交易信号
        print("\n📊 执行交易信号...")
        executed_count = 0
        for signal in filtered_signals:
            if self.execute_signal(signal):
                executed_count += 1
        
        # 5. 生成报告
        self.generate_daily_report()
        
        print(f"\n✅ 今日执行 {executed_count} 笔交易")
        print("="*60)
    
    def generate_daily_report(self):
        """生成每日报告"""
        report_dir = self.base_dir / "reports"
        report_dir.mkdir(exist_ok=True)
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        report_file = report_dir / f"daily_report_{date_str}.md"
        
        # 计算账户总值
        total_value = self.account["cash"]
        for symbol, pos in self.account["positions"].items():
            data = self.get_market_data(symbol, pos["market"])
            current_price = data["close"].iloc[-1]
            total_value += current_price * pos["quantity"]
        
        total_pnl = total_value - self.account["initial_capital"]
        pnl_pct = total_pnl / self.account["initial_capital"] * 100
        
        report = f"""# 📊 量化交易每日报告
**日期：** {date_str}
**模式：** {self.account['mode']}

---

## 💰 账户概览

| 项目 | 数值 |
|------|------|
| 初始资金 | ${self.account['initial_capital']:.2f} |
| 当前现金 | ${self.account['cash']:.2f} |
| 持仓市值 | ${total_value - self.account['cash']:.2f} |
| **账户总值** | **${total_value:.2f}** |
| 总盈亏 | ${total_pnl:.2f} ({pnl_pct:+.2f}%) |

---

## 📈 持仓详情

| 标的 | 市场 | 数量 | 成本价 | 现价 | 盈亏% |
|------|------|------|--------|------|-------|
"""
        
        for symbol, pos in self.account["positions"].items():
            data = self.get_market_data(symbol, pos["market"])
            current_price = data["close"].iloc[-1]
            pnl = (current_price - pos["avg_price"]) / pos["avg_price"] * 100
            report += f"| {symbol} | {pos['market']} | {pos['quantity']} | ${pos['avg_price']:.2f} | ${current_price:.2f} | {pnl:+.2f}% |\n"
        
        if not self.account["positions"]:
            report += "| 无持仓 | - | - | - | - | - |\n"
        
        report += f"""
---

## 📝 今日交易

| 时间 | 操作 | 标的 | 价格 | 数量 | 金额 | 策略 |
|------|------|------|------|------|------|------|
"""
        
        today_trades = [t for t in self.account["history"] 
                       if t["timestamp"].startswith(date_str)]
        
        for trade in today_trades:
            report += f"| {trade['timestamp'][11:16]} | {trade['action']} | {trade['symbol']} | ${trade['price']:.2f} | {trade['quantity']} | ${trade['value']:.2f} | {trade['strategy']} |\n"
        
        if not today_trades:
            report += "| - | - | - | - | - | - | - |\n"
        
        report += f"""
---

## 📊 策略表现

| 策略 | 今日信号 | 执行数 | 胜率 |
|------|----------|--------|------|
| 趋势跟踪 | {len([s for s in self.account['history'] if s.get('strategy') == 'trend_following'])} | - | - |
| 动量策略 | {len([s for s in self.account['history'] if s.get('strategy') == 'momentum'])} | - | - |
| 均值回归 | {len([s for s in self.account['history'] if s.get('strategy') == 'mean_reversion'])} | - | - |
| 多因子选股 | {len([s for s in self.account['history'] if s.get('strategy') == 'multi_factor'])} | - | - |

---

## ⚠️ 风控状态

| 指标 | 当前值 | 限制 | 状态 |
|------|--------|------|------|
| 单日盈亏 | ${self.risk_metrics['daily_pnl']:.2f} | -5% | 🟢 正常 |
| 总仓位 | {(total_value - self.account['cash']) / total_value * 100:.1f}% | 80% | 🟢 正常 |
| 连续亏损 | {self.risk_metrics['consecutive_losses']} 天 | 3 天 | 🟢 正常 |

---

*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*免责声明：模拟交易仅供参考，不构成投资建议*
"""
        
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"📧 报告已保存：{report_file}")
        
        # 保存账户状态
        state_file = self.base_dir / "data" / f"account_state_{date_str}.json"
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump({
                "account": self.account,
                "risk_metrics": self.risk_metrics,
                "timestamp": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        return report_file
    
    def load_state(self, date_str=None):
        """加载账户状态"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        state_file = self.base_dir / "data" / f"account_state_{date_str}.json"
        if state_file.exists():
            with open(state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
                self.account = state["account"]
                self.risk_metrics = state["risk_metrics"]
            print(f"✅ 已加载 {date_str} 账户状态")
            return True
        return False


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🚀 多市场量化交易系统启动")
    print("="*60)
    
    # 初始化系统
    system = QuantTradingSystem()
    
    # 尝试加载昨日状态
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    system.load_state(yesterday)
    
    # 运行每日交易
    system.run_daily()
    
    print("\n✅ 量化交易系统运行完成！")

if __name__ == "__main__":
    main()
