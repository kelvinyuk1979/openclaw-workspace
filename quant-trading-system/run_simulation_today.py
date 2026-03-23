#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股量化交易模拟运行 - 使用模拟数据演示
日期：2026-03-17
"""

import json
import random
from datetime import datetime
from pathlib import Path

# 配置
CONFIG_PATH = Path(__file__).parent / "config" / "config.json"
DATA_PATH = Path(__file__).parent / "data"
REPORTS_PATH = Path(__file__).parent / "reports"

def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_mock_data(stock_code, config):
    """生成模拟股票数据（用于演示）"""
    random.seed(hash(stock_code + "2026-03-17") % 2**32)
    
    # 基准价格（根据不同股票类型）
    base_prices = {
        "600519": 1480.0,  # 贵州茅台
        "300750": 395.0,   # 宁德时代
        "002594": 108.0,   # 比亚迪
        "000858": 42.0,    # 五粮液
        "000333": 58.0,    # 美的集团
        "601318": 68.0,    # 中国平安
        "600036": 42.0,    # 招商银行
        "600276": 95.0,    # 恒瑞医药
        "600030": 22.0,    # 中信证券
        "601888": 58.0,    # 中国中免
        "300059": 18.0,    # 东方财富
        "300014": 52.0,    # 亿纬锂能
        "300122": 28.0,    # 智飞生物
        "300124": 38.0,    # 汇川技术
        "300274": 85.0,    # 阳光电源
        "300308": 95.0,    # 中际旭创
        "300413": 38.0,    # 芒果超媒
        "300433": 28.0,    # 蓝思科技
        "300498": 18.0,    # 温氏股份
        "300601": 42.0,    # 康泰生物
    }
    
    base_price = base_prices.get(stock_code, 50.0)
    
    # 生成今日价格（±3% 波动）
    change_pct = random.uniform(-0.03, 0.03)
    current_price = base_price * (1 + change_pct)
    
    # 生成技术指标
    rsi = random.uniform(25, 75)
    ma5 = base_price * random.uniform(0.98, 1.02)
    ma20 = base_price * random.uniform(0.95, 1.05)
    
    # 成交量（相对均量的倍数）
    volume_ratio = random.uniform(0.8, 2.5)
    
    return {
        "code": stock_code,
        "price": round(current_price, 2),
        "change_pct": round(change_pct * 100, 2),
        "rsi": round(rsi, 2),
        "ma5": round(ma5, 2),
        "ma20": round(ma20, 2),
        "volume_ratio": round(volume_ratio, 2),
    }

def analyze_signal(stock_data, config):
    """根据策略分析交易信号"""
    strategies = config["strategies"]
    signals = {"LONG": 0, "SHORT": 0, "HOLD": 0}
    
    rsi = stock_data["rsi"]
    price = stock_data["price"]
    ma5 = stock_data["ma5"]
    ma20 = stock_data["ma20"]
    volume_ratio = stock_data["volume_ratio"]
    
    # 趋势跟踪策略 (35%)
    if strategies["trend_following"]["enabled"]:
        if price > ma5 > ma20 and rsi > 50:
            signals["LONG"] += 1
        elif price < ma5 < ma20 and rsi < 50:
            signals["SHORT"] += 1
        else:
            signals["HOLD"] += 1
    
    # 动量策略 (35%)
    if strategies["momentum"]["enabled"]:
        if rsi < 40 and volume_ratio > 1.5:
            signals["LONG"] += 1  # 超卖 + 放量
        elif rsi > 60 and volume_ratio > 1.5:
            signals["SHORT"] += 1  # 超买 + 放量
        else:
            signals["HOLD"] += 1
    
    # 均值回归策略 (30%)
    if strategies["mean_reversion"]["enabled"]:
        if rsi < 30:
            signals["LONG"] += 1  # 极度超卖
        elif rsi > 70:
            signals["SHORT"] += 1  # 极度超买
        else:
            signals["HOLD"] += 1
    
    # 决策
    if signals["LONG"] >= 2:
        return "BUY", signals
    elif signals["SHORT"] >= 2:
        return "SELL", signals
    else:
        return "HOLD", signals

def run_simulation():
    """运行模拟交易"""
    print("\n" + "="*60)
    print("📊 A 股量化交易模拟系统 - 2026-03-17")
    print("="*60)
    
    config = load_config()
    account = {
        "initial_capital": config["account"]["initial_capital"],
        "cash": config["account"]["initial_capital"],
        "positions": {},
        "history": [],
    }
    
    # 加载昨日状态（如果有）
    yesterday_file = DATA_PATH / "account_state_2026-03-16.json"
    if yesterday_file.exists():
        with open(yesterday_file, 'r', encoding='utf-8') as f:
            yesterday = json.load(f)
            account["cash"] = yesterday["account"]["cash"]
            account["positions"] = yesterday["account"]["positions"]
            account["history"] = yesterday["account"]["history"]
    
    print(f"\n💰 初始资金：¥{account['initial_capital']:,.2f}")
    print(f"💵 当前现金：¥{account['cash']:,.2f}")
    print(f"📈 持仓数量：{len(account['positions'])}")
    
    # 扫描股票池
    stock_pool = []
    for category in ["large_cap", "growth", "niche_leader"]:
        stock_pool.extend(config["a_stock_pool"][category])
    
    print(f"\n🔍 扫描股票池：{len(stock_pool)} 只股票")
    print("-"*60)
    
    trades = []
    signals_summary = []
    
    for stock_code in stock_pool[:15]:  # 只分析前 15 只
        data = generate_mock_data(stock_code, config)
        signal, signals = analyze_signal(data, config)
        
        if signal != "HOLD":
            signals_summary.append({
                "code": stock_code,
                "signal": signal,
                "price": data["price"],
                "rsi": data["rsi"],
                "votes": signals,
            })
    
    # 执行交易（模拟）
    print("\n📊 生成的交易信号：")
    print("-"*60)
    
    for sig in signals_summary:
        vote_str = f"LONG:{sig['votes']['LONG']} SHORT:{sig['votes']['SHORT']} HOLD:{sig['votes']['HOLD']}"
        print(f"  {sig['code']} | {sig['signal']:4} | ¥{sig['price']:>8.2f} | RSI:{sig['rsi']:5.1f} | {vote_str}")
    
    # 选择最强的买入信号（最多 2 只）
    buy_signals = [s for s in signals_summary if s["signal"] == "BUY"]
    buy_signals.sort(key=lambda x: x["votes"]["LONG"], reverse=True)
    
    max_positions = config["risk_control"]["position_single_max"]
    single_max_pct = max_positions
    
    print("\n" + "="*60)
    print("📝 今日交易执行：")
    print("-"*60)
    
    for sig in buy_signals[:2]:  # 最多买 2 只
        position_size = account["cash"] * single_max_pct
        shares = int(position_size / sig["price"] / 100) * 100  # 100 股整数倍
        
        if shares > 0:
            cost = shares * sig["price"]
            commission = max(5, cost * 0.0003)
            total_cost = cost + commission
            
            if total_cost <= account["cash"]:
                account["cash"] -= total_cost
                account["positions"][sig["code"]] = {
                    "shares": shares,
                    "cost_price": sig["price"],
                    "cost_total": total_cost,
                    "date": "2026-03-17",
                }
                
                trades.append({
                    "time": "15:00",
                    "action": "BUY",
                    "code": sig["code"],
                    "price": sig["price"],
                    "shares": shares,
                    "cost": total_cost,
                    "strategy": "multi_strategy_vote",
                })
                
                print(f"  ✅ 买入 {sig['code']} | {shares}股 @ ¥{sig['price']:.2f} | 总计 ¥{total_cost:,.2f}")
    
    if not trades:
        print("  ⚠️  今日无符合条件的交易信号")
    
    # 计算账户总值
    total_value = account["cash"]
    for code, pos in account["positions"].items():
        # 模拟当前价格（成本价 ±2%）
        random.seed(hash(code + "2026-03-17-close") % 2**32)
        current_price = pos["cost_price"] * (1 + random.uniform(-0.02, 0.02))
        market_value = pos["shares"] * current_price
        total_value += market_value
    
    pnl = total_value - account["initial_capital"]
    pnl_pct = pnl / account["initial_capital"] * 100
    
    # 保存状态
    account_state = {
        "account": account,
        "risk_metrics": {
            "daily_pnl": pnl,
            "weekly_pnl": pnl,
            "monthly_pnl": pnl,
            "total_pnl": pnl,
            "consecutive_losses": 0 if pnl >= 0 else 1,
        },
        "timestamp": datetime.now().isoformat(),
    }
    
    today_file = DATA_PATH / "account_state_2026-03-17.json"
    with open(today_file, 'w', encoding='utf-8') as f:
        json.dump(account_state, f, ensure_ascii=False, indent=2)
    
    # 生成报告
    report = f"""# 📊 A 股量化交易每日报告
**日期：** 2026-03-17
**模式：** simulation

---

## 💰 账户概览

| 项目 | 数值 |
|------|------|
| 初始资金 | ¥{account['initial_capital']:,.2f} |
| 当前现金 | ¥{account['cash']:,.2f} |
| 持仓市值 | ¥{total_value - account['cash']:,.2f} |
| **账户总值** | **¥{total_value:,.2f}** |
| 总盈亏 | ¥{pnl:+,.2f} ({pnl_pct:+.2f}%) |

---

## 📈 持仓详情

| 标的 | 数量 | 成本价 | 市值 | 盈亏% |
|------|------|--------|------|-------|
"""
    
    if account["positions"]:
        for code, pos in account["positions"].items():
            random.seed(hash(code + "2026-03-17-close") % 2**32)
            current_price = pos["cost_price"] * (1 + random.uniform(-0.02, 0.02))
            market_value = pos["shares"] * current_price
            pnl_pos = (current_price - pos["cost_price"]) / pos["cost_price"] * 100
            report += f"| {code} | {pos['shares']} | ¥{pos['cost_price']:.2f} | ¥{market_value:,.2f} | {pnl_pos:+.2f}% |\n"
    else:
        report += "| 无持仓 | - | - | - | - |\n"
    
    report += f"""
---

## 📝 今日交易

| 时间 | 操作 | 标的 | 价格 | 数量 | 金额 | 策略 |
|------|------|------|------|------|------|------|
"""
    
    if trades:
        for t in trades:
            report += f"| {t['time']} | {t['action']} | {t['code']} | ¥{t['price']:.2f} | {t['shares']} | ¥{t['cost']:,.2f} | {t['strategy']} |\n"
    else:
        report += "| - | - | - | - | - | - | - |\n"
    
    report += f"""
---

## ⚠️ 风控状态

| 指标 | 当前值 | 限制 | 状态 |
|------|--------|------|------|
| 单日盈亏 | ¥{pnl:+,.2f} | -5% | {'🟢 正常' if pnl > -account['initial_capital']*0.05 else '🔴 触及'} |
| 总仓位 | {(total_value - account['cash'])/total_value*100:.1f}% | 95% | 🟢 正常 |
| T+1 限制 | {len(trades)}只 | - | 🟢 正常 |

---

## 📊 策略信号汇总

今日扫描 {len(stock_pool)} 只股票，生成 {len(signals_summary)} 个交易信号：

"""
    
    for sig in signals_summary:
        vote_str = f"多:{sig['votes']['LONG']} 空:{sig['votes']['SHORT']} 平:{sig['votes']['HOLD']}"
        report += f"- **{sig['code']}**: {sig['signal']} @ ¥{sig['price']:.2f} (RSI:{sig['rsi']:.1f}, {vote_str})\n"
    
    report += f"""
---

*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*免责声明：模拟交易仅供参考，不构成投资建议*
"""
    
    report_file = REPORTS_PATH / "daily_report_2026-03-17.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 交易完成！")
    print(f"📊 账户总值：¥{total_value:,.2f} ({pnl_pct:+.2f}%)")
    print(f"📧 报告已保存：{report_file}")
    print("="*60)

if __name__ == "__main__":
    run_simulation()
