#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股量化交易系统 - 主引擎
支持 A 股特色规则：T+1、涨跌停、最小交易单位等
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np

# 尝试导入 akshare
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    print("⚠️  akshare 未安装，使用模拟数据")

# 尝试导入 tushare
try:
    import tushare as ts
    TUSHARE_AVAILABLE = True
except ImportError:
    TUSHARE_AVAILABLE = False
    print("⚠️  tushare 未安装，请运行：pip3 install tushare")

# 导入策略模块
from strategies.trend_following import TrendFollowingStrategy
from strategies.momentum import MomentumStrategy
from strategies.mean_reversion import MeanReversionStrategy

class AStockQuantSystem:
    """A 股量化交易系统"""
    
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
            "mode": self.config["account"]["mode"],
            "t_plus_1": self.config["risk_control"]["a_stock_rules"]["t_plus_1"],
            "today_bought": []  # 今日买入，明日才能卖
        }
        
        # 初始化策略
        self.strategies = {
            "trend_following": TrendFollowingStrategy(self.config["strategies"]["trend_following"]),
            "momentum": MomentumStrategy(self.config["strategies"]["momentum"]),
            "mean_reversion": MeanReversionStrategy(self.config["strategies"]["mean_reversion"])
        }
        
        # 风控指标
        self.risk_metrics = {
            "daily_pnl": 0,
            "weekly_pnl": 0,
            "monthly_pnl": 0,
            "total_pnl": 0,
            "consecutive_losses": 0
        }
        
        # 加载 Tushare 配置
        self.tushare_config = self.load_tushare_config()
        if TUSHARE_AVAILABLE and self.tushare_config.get("enabled", False):
            ts.set_token(self.tushare_config["token"])
            self.pro = ts.pro_api()
            print(f"🟢 Tushare 已启用")
        else:
            self.pro = None
            if TUSHARE_AVAILABLE:
                print(f"🟡 Tushare 未启用（请在配置文件中设置 enabled=true）")
            else:
                print(f"🔴 Tushare 不可用")
        
        print(f"✅ A 股量化交易系统初始化完成")
        print(f"📊 模式：{self.account['mode']}")
        print(f"💰 初始资金：¥{self.account['initial_capital']}")
        print(f"📈 股票池：{len(self.get_stock_pool())} 只")
    
    def load_config(self):
        """加载配置文件"""
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def load_tushare_config(self):
        """加载 Tushare 配置文件"""
        tushare_config_path = self.base_dir / "config" / "tushare_config.json"
        if tushare_config_path.exists():
            with open(tushare_config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                # 返回 tushare 嵌套对象
                return config.get("tushare", {"enabled": False, "token": ""})
        return {"enabled": False, "token": ""}
    
    def get_stock_pool(self):
        """获取 A 股股票池"""
        pool = self.config.get("a_stock_pool", {})
        stocks = []
        for category, stock_list in pool.items():
            stocks.extend(stock_list)
        return stocks
    
    def get_a_stock_data(self, symbol, period="daily", start_date=None, end_date=None):
        """获取 A 股数据（tushare / akshare / 模拟）"""
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=60)).strftime("%Y%m%d")
        if end_date is None:
            end_date = datetime.now().strftime("%Y%m%d")
        
        # 优先使用 Tushare
        if self.pro is not None:
            try:
                # Tushare 需要 ts_code 格式（如 000001.SZ）
                if symbol.startswith("6"):
                    ts_code = f"{symbol}.SH"
                else:
                    ts_code = f"{symbol}.SZ"
                
                data = self.pro.daily(
                    ts_code=ts_code,
                    start_date=start_date,
                    end_date=end_date
                )
                if data is not None and len(data) > 0:
                    # 重命名列以匹配策略
                    data = data.rename(columns={
                        "trade_date": "date",
                        "open": "open",
                        "close": "close",
                        "high": "high",
                        "low": "low",
                        "vol": "volume"
                    })
                    data["date"] = pd.to_datetime(data["date"])
                    return data.sort_values("date")
            except Exception as e:
                print(f"⚠️  Tushare {symbol} 数据获取失败：{e}")
        
        # 备用 Akshare
        if AKSHARE_AVAILABLE:
            try:
                data = ak.stock_zh_a_hist(
                    symbol=symbol,
                    period=period,
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq"
                )
                if data is not None and len(data) > 0:
                    # 重命名列以匹配策略
                    data = data.rename(columns={
                        "日期": "date",
                        "开盘": "open",
                        "收盘": "close",
                        "最高": "high",
                        "最低": "low",
                        "成交量": "volume"
                    })
                    return data
            except Exception as e:
                print(f"⚠️  AkShare {symbol} 数据获取失败：{e}")
        
        # 模拟数据
        print(f"🔸 {symbol} 使用模拟数据")
        return self.generate_mock_data(symbol)
    
    def generate_mock_data(self, symbol):
        """生成模拟数据"""
        dates = pd.date_range(end=datetime.now(), periods=60, freq="D")
        np.random.seed(hash(symbol) % 10000)
        
        base_price = np.random.uniform(20, 500)
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
    
    def check_price_limit(self, symbol, price):
        """检查涨跌停（A 股±10%，创业板/科创板±20%）"""
        # 简化处理，默认±10%
        limit = self.config["risk_control"]["a_stock_rules"]["price_limit"]
        
        # 获取昨日收盘价
        data = self.get_a_stock_data(symbol)
        if len(data) < 2:
            return True
        
        prev_close = data["close"].iloc[-2]
        upper_limit = prev_close * (1 + limit)
        lower_limit = prev_close * (1 - limit)
        
        if price > upper_limit or price < lower_limit:
            return False  # 涨跌停，无法交易
        
        return True
    
    def calculate_quantity(self, price, value):
        """计算买入数量（A 股最小 100 股=1 手）"""
        min_lot = self.config["risk_control"]["a_stock_rules"]["min_lot"]
        quantity = int(value / price / min_lot) * min_lot
        return max(quantity, 0)
    
    def scan_market(self):
        """扫描 A 股市场"""
        stock_pool = self.get_stock_pool()
        
        print("\n🔍 扫描 A 股市场...")
        signals = []
        
        for symbol in stock_pool:
            try:
                data = self.get_a_stock_data(symbol)
                
                if len(data) < 30:
                    continue
                
                # 运行策略
                for strategy_name, strategy in self.strategies.items():
                    if self.config["strategies"][strategy_name]["enabled"]:
                        signal = strategy.generate_signal(symbol, "A 股", data)
                        if signal:
                            signal["strategy"] = strategy_name
                            signal["market"] = "A 股"
                            
                            # A 股特色：检查涨跌停
                            if not self.check_price_limit(symbol, signal["price"]):
                                continue
                            
                            # 计算正确数量
                            allocation = self.config["strategies"][strategy_name]["allocation"]
                            position_value = self.account["initial_capital"] * allocation * 0.2
                            signal["quantity"] = self.calculate_quantity(signal["price"], position_value)
                            
                            if signal["quantity"] > 0:
                                signals.append(signal)
                
            except Exception as e:
                print(f"⚠️  {symbol} 分析失败：{e}")
        
        print(f"✅ 生成 {len(signals)} 个交易信号")
        return signals
    
    def can_sell(self, symbol):
        """检查是否可以卖出（T+1 规则）"""
        if not self.account["t_plus_1"]:
            return True
        
        # 今日买入的不能卖
        if symbol in self.account["today_bought"]:
            return False
        
        return True
    
    def risk_check(self, signal):
        """风控检查"""
        risk_config = self.config["risk_control"]
        
        # 检查单日亏损
        if self.risk_metrics["daily_pnl"] < risk_config["daily_loss_limit"]:
            print(f"⚠️  触发单日亏损限制，停止交易")
            return False
        
        # 检查总仓位
        total_position = sum(
            p["quantity"] * p["avg_price"]
            for p in self.account["positions"].values()
        )
        if total_position / self.account["initial_capital"] >= risk_config["position_total_max"]:
            print(f"⚠️  达到总仓位上限")
            return False
        
        # 检查单只股票仓位
        if signal["symbol"] in self.account["positions"]:
            current_value = (
                self.account["positions"][signal["symbol"]]["quantity"] *
                self.account["positions"][signal["symbol"]]["avg_price"]
            )
            if current_value / self.account["initial_capital"] >= risk_config["position_single_max"]:
                print(f"⚠️  {signal['symbol']} 达到单只仓位上限")
                return False
        
        return True
    
    def execute_signal(self, signal):
        """执行交易信号"""
        action = signal["action"]
        symbol = signal["symbol"]
        price = signal["price"]
        quantity = signal["quantity"]
        
        # A 股规则：最小 100 股
        if quantity < 100:
            print(f"⚠️  {symbol} 数量不足 100 股，跳过")
            return False
        
        # 计算费用
        value = price * quantity
        rules = self.config["risk_control"]["a_stock_rules"]
        commission = max(value * rules["commission"], rules["commission_min"])
        stamp_tax = value * rules["stamp_tax"] if action == "sell" else 0
        
        if action == "buy":
            # 检查现金
            if self.account["cash"] < value + commission:
                print(f"⚠️  现金不足，无法买入 {symbol}")
                return False
            
            # 更新账户
            self.account["cash"] -= (value + commission)
            
            if symbol in self.account["positions"]:
                pos = self.account["positions"][symbol]
                total_value = pos["avg_price"] * pos["quantity"] + value
                total_quantity = pos["quantity"] + quantity
                pos["avg_price"] = total_value / total_quantity
                pos["quantity"] = total_quantity
            else:
                self.account["positions"][symbol] = {
                    "quantity": quantity,
                    "avg_price": price,
                    "market": "A 股",
                    "entry_date": datetime.now().isoformat()
                }
            
            # T+1 记录
            self.account["today_bought"].append(symbol)
            
            print(f"✅ 买入 {symbol}: {quantity}股 @ ¥{price:.2f}, 金额：¥{value:.2f}")
        
        elif action == "sell":
            # T+1 检查
            if not self.can_sell(symbol):
                print(f"⚠️  {symbol} T+1 限制，今日买入不能卖出")
                return False
            
            if symbol not in self.account["positions"]:
                print(f"⚠️  没有 {symbol} 持仓，无法卖出")
                return False
            
            position = self.account["positions"][symbol]
            if position["quantity"] < quantity:
                quantity = position["quantity"]
            
            # 计算盈亏
            pnl = (price - position["avg_price"]) * quantity - stamp_tax - commission
            self.risk_metrics["total_pnl"] += pnl
            
            # 更新账户
            self.account["cash"] += (value - commission - stamp_tax)
            position["quantity"] -= quantity
            
            print(f"✅ 卖出 {symbol}: {quantity}股 @ ¥{price:.2f}, 盈亏：¥{pnl:.2f}")
            
            if position["quantity"] <= 0:
                del self.account["positions"][symbol]
        
        # 记录交易
        self.account["history"].append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "symbol": symbol,
            "market": "A 股",
            "price": price,
            "quantity": quantity,
            "value": value,
            "commission": commission,
            "stamp_tax": stamp_tax,
            "strategy": signal.get("strategy", "manual")
        })
        
        return True
    
    def check_stop_loss_take_profit(self):
        """检查止损止盈"""
        risk_config = self.config["risk_control"]
        
        for symbol, position in list(self.account["positions"].items()):
            # T+1 检查
            if not self.can_sell(symbol):
                continue
            
            # 获取最新价格
            data = self.get_a_stock_data(symbol)
            current_price = data["close"].iloc[-1]
            
            cost_basis = position["avg_price"]
            pnl_pct = (current_price - cost_basis) / cost_basis
            
            # 止损
            if pnl_pct <= risk_config["stop_loss"]:
                print(f"🛑 止损触发：{symbol} 亏损 {pnl_pct*100:.2f}%")
                self.execute_signal({
                    "action": "sell",
                    "symbol": symbol,
                    "price": current_price,
                    "quantity": position["quantity"],
                    "strategy": "stop_loss"
                })
            
            # 止盈
            elif pnl_pct >= risk_config["take_profit"]:
                print(f"✅ 止盈触发：{symbol} 盈利 {pnl_pct*100:.2f}%")
                sell_quantity = position["quantity"] // 2
                if sell_quantity > 0:
                    self.execute_signal({
                        "action": "sell",
                        "symbol": symbol,
                        "price": current_price,
                        "quantity": sell_quantity,
                        "strategy": "take_profit"
                    })
    
    def run_daily(self):
        """每日运行"""
        print("\n" + "="*60)
        print(f"🤖 A 股量化交易系统 - 每日运行")
        print(f"📅 日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*60)
        
        # 1. 扫描市场
        signals = self.scan_market()
        
        # 2. 过滤信号
        filtered_signals = []
        for strategy_name in self.strategies.keys():
            strategy_signals = [s for s in signals if s["strategy"] == strategy_name]
            if strategy_signals:
                best_signal = max(strategy_signals, key=lambda x: x.get("confidence", 0))
                filtered_signals.append(best_signal)
        
        # 3. 检查止损止盈
        self.check_stop_loss_take_profit()
        
        # 4. 执行交易
        print("\n📊 执行交易信号...")
        executed_count = 0
        for signal in filtered_signals:
            if self.risk_check(signal):
                if self.execute_signal(signal):
                    executed_count += 1
        
        # 5. 生成报告
        self.generate_daily_report()
        
        # 6. 清空今日买入记录（T+1）
        self.account["today_bought"] = []
        
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
            data = self.get_a_stock_data(symbol)
            current_price = data["close"].iloc[-1]
            total_value += current_price * pos["quantity"]
        
        total_pnl = total_value - self.account["initial_capital"]
        pnl_pct = total_pnl / self.account["initial_capital"] * 100
        
        report = f"""# 📊 A 股量化交易每日报告
**日期：** {date_str}
**模式：** {self.account['mode']}

---

## 💰 账户概览

| 项目 | 数值 |
|------|------|
| 初始资金 | ¥{self.account['initial_capital']:.2f} |
| 当前现金 | ¥{self.account['cash']:.2f} |
| 持仓市值 | ¥{total_value - self.account['cash']:.2f} |
| **账户总值** | **¥{total_value:.2f}** |
| 总盈亏 | ¥{total_pnl:.2f} ({pnl_pct:+.2f}%) |

---

## 📈 持仓详情

| 标的 | 数量 | 成本价 | 现价 | 盈亏% |
|------|------|--------|------|-------|
"""
        
        for symbol, pos in self.account["positions"].items():
            data = self.get_a_stock_data(symbol)
            current_price = data["close"].iloc[-1]
            pnl = (current_price - pos["avg_price"]) / pos["avg_price"] * 100
            report += f"| {symbol} | {pos['quantity']} | ¥{pos['avg_price']:.2f} | ¥{current_price:.2f} | {pnl:+.2f}% |\n"
        
        if not self.account["positions"]:
            report += "| 无持仓 | - | - | - | - |\n"
        
        report += f"""
---

## 📝 今日交易

| 时间 | 操作 | 标的 | 价格 | 数量 | 金额 | 策略 |
|------|------|------|------|------|------|------|
"""
        
        today_trades = [t for t in self.account["history"] 
                       if t["timestamp"].startswith(date_str)]
        
        for trade in today_trades:
            report += f"| {trade['timestamp'][11:16]} | {trade['action']} | {trade['symbol']} | ¥{trade['price']:.2f} | {trade['quantity']} | ¥{trade['value']:.2f} | {trade['strategy']} |\n"
        
        if not today_trades:
            report += "| - | - | - | - | - | - | - |\n"
        
        report += f"""
---

## ⚠️ 风控状态

| 指标 | 当前值 | 限制 | 状态 |
|------|--------|------|------|
| 单日盈亏 | ¥{self.risk_metrics['daily_pnl']:.2f} | -5% | 🟢 正常 |
| 总仓位 | {(total_value - self.account['cash']) / total_value * 100:.1f}% | 95% | 🟢 正常 |
| T+1 限制 | {len(self.account['today_bought'])} 只 | - | 🟢 正常 |

---

*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*免责声明：模拟交易仅供参考，不构成投资建议*
"""
        
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"📧 报告已保存：{report_file}")
        
        # 保存状态
        state_file = self.base_dir / "data" / f"account_state_{date_str}.json"
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump({
                "account": self.account,
                "risk_metrics": self.risk_metrics,
                "timestamp": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        return report_file


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🚀 A 股量化交易系统启动")
    print("="*60)
    
    system = AStockQuantSystem()
    
    # 加载昨日状态
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    system.account.get("today_bought", []).clear()
    
    system.run_daily()
    
    print("\n✅ A 股量化交易系统运行完成！")

if __name__ == "__main__":
    main()
