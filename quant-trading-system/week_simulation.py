#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股量化交易 - 一周回测模拟
模拟一周交易，生成每日盈利报告
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# 配置
INITIAL_CAPITAL = 10000
COMMISSION_RATE = 0.0003  # 万 3
COMMISSION_MIN = 5  # 最低 5 元
STAMP_TAX = 0.0005  # 印花税 0.05%

# 股票池
STOCK_POOL = [
    "600519", "300750", "002594", "000858", "000333",
    "601318", "600036", "600276", "600030", "601888",
    "300059", "300014", "300122", "300124", "300274",
    "300308", "300413", "300433", "300498", "300601",
    "688012", "688111", "688390", "300763", "300861",
    "688122", "688016", "300723", "688180", "688981"
]

def generate_week_prices():
    """生成一周的股票价格数据（模拟）"""
    np.random.seed(42)  # 固定种子，可复现
    
    week_data = {}
    base_date = datetime(2026, 3, 16)  # 周一
    
    # 生成 5 个交易日
    for day in range(5):
        date = base_date + timedelta(days=day)
        if date.weekday() >= 5:  # 跳过周末
            date += timedelta(days=2)
        
        date_str = date.strftime("%Y-%m-%d")
        week_data[date_str] = {}
        
        for symbol in STOCK_POOL:
            np.random.seed(hash(symbol + date_str) % 100000)
            
            # 生成价格
            base_price = np.random.uniform(20, 500)
            daily_change = np.random.normal(0.002, 0.03)  # 日均 0.2% 收益，波动 3%
            
            week_data[date_str][symbol] = {
                "open": base_price,
                "close": base_price * (1 + daily_change),
                "high": base_price * (1 + abs(np.random.normal(0, 0.02))),
                "low": base_price * (1 - abs(np.random.normal(0, 0.02))),
                "volume": np.random.randint(100000, 10000000)
            }
    
    return week_data

def calculate_signal(symbol, data, prev_data=None, day_index=0):
    """生成交易信号（更积极）"""
    np.random.seed(hash(symbol) % 10000 + day_index)
    
    # 30% 概率产生买入信号
    if np.random.random() < 0.3:
        return {"action": "buy", "confidence": 0.7}
    
    return None

def run_week_simulation():
    """运行一周模拟交易"""
    print("\n" + "="*70)
    print("📊 A 股量化交易 - 一周模拟回测")
    print("="*70)
    
    # 生成数据
    week_data = generate_week_prices()
    dates = sorted(week_data.keys())
    
    # 账户状态
    account = {
        "cash": INITIAL_CAPITAL,
        "positions": {},
        "history": [],
        "daily_values": []
    }
    
    print(f"\n💰 初始资金：¥{INITIAL_CAPITAL:,.2f}")
    print(f"📈 股票池：{len(STOCK_POOL)} 只")
    print(f"📅 交易日期：{dates[0]} 至 {dates[-1]}")
    print("\n" + "-"*70)
    
    # 每日交易
    for i, date_str in enumerate(dates):
        print(f"\n📅 第{i+1}天：{date_str}")
        print("-"*70)
        
        day_trades = []
        day_pnl = 0
        
        # 获取今日和昨日数据
        today_data = week_data[date_str]
        prev_data = week_data[dates[i-1]] if i > 0 else None
        
        # 检查持仓盈亏
        for symbol, pos in list(account["positions"].items()):
            if symbol in today_data:
                current_price = today_data[symbol]["close"]
                pnl = (current_price - pos["avg_price"]) * pos["quantity"]
                day_pnl += pnl
        
        # 生成交易信号
        for symbol in STOCK_POOL[:10]:  # 每天分析前 10 只
            signal = calculate_signal(symbol, today_data.get(symbol, {}), 
                                     prev_data.get(symbol, {}) if prev_data else None, i)
            
            if signal:
                price = today_data.get(symbol, {}).get("close", 0)
                if price <= 0:
                    continue
                
                # 执行交易
                if signal["action"] == "buy" and account["cash"] > price * 100:
                    # 买入（100 股=1 手）
                    quantity = 100
                    value = price * quantity
                    commission = max(value * COMMISSION_RATE, COMMISSION_MIN)
                    
                    if account["cash"] >= value + commission:
                        account["cash"] -= (value + commission)
                        
                        if symbol in account["positions"]:
                            pos = account["positions"][symbol]
                            total_value = pos["avg_price"] * pos["quantity"] + value
                            total_qty = pos["quantity"] + quantity
                            pos["avg_price"] = total_value / total_qty
                            pos["quantity"] = total_qty
                        else:
                            account["positions"][symbol] = {
                                "quantity": quantity,
                                "avg_price": price
                            }
                        
                        day_trades.append({
                            "action": "buy",
                            "symbol": symbol,
                            "price": price,
                            "quantity": quantity,
                            "value": value,
                            "commission": commission
                        })
                
                elif signal["action"] == "sell" and symbol in account["positions"]:
                    # 卖出
                    pos = account["positions"][symbol]
                    quantity = pos["quantity"]
                    value = price * quantity
                    commission = max(value * COMMISSION_RATE, COMMISSION_MIN)
                    stamp_tax = value * STAMP_TAX
                    
                    pnl = (price - pos["avg_price"]) * quantity - commission - stamp_tax
                    day_pnl += pnl
                    
                    account["cash"] += (value - commission - stamp_tax)
                    
                    day_trades.append({
                        "action": "sell",
                        "symbol": symbol,
                        "price": price,
                        "quantity": quantity,
                        "value": value,
                        "commission": commission,
                        "stamp_tax": stamp_tax,
                        "pnl": pnl
                    })
                    
                    del account["positions"][symbol]
        
        # 计算账户总值
        total_value = account["cash"]
        for symbol, pos in account["positions"].items():
            if symbol in today_data:
                total_value += today_data[symbol]["close"] * pos["quantity"]
        
        account["daily_values"].append({
            "date": date_str,
            "cash": account["cash"],
            "positions_value": total_value - account["cash"],
            "total_value": total_value,
            "pnl": total_value - INITIAL_CAPITAL,
            "pnl_pct": (total_value - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100,
            "trades": len(day_trades),
            "day_pnl": day_pnl
        })
        
        # 打印当日结果
        print(f"  现金：¥{account['cash']:,.2f}")
        print(f"  持仓：{len(account['positions'])} 只")
        print(f"  总值：¥{total_value:,.2f}")
        print(f"  盈亏：¥{total_value - INITIAL_CAPITAL:,.2f} ({(total_value - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100:+.2f}%)")
        print(f"  交易：{len(day_trades)} 笔")
        
        if day_trades:
            for trade in day_trades[:3]:  # 只显示前 3 笔
                if trade["action"] == "buy":
                    print(f"    🟢 买入 {trade['symbol']}: {trade['quantity']}股 @ ¥{trade['price']:.2f}")
                else:
                    print(f"    🔴 卖出 {trade['symbol']}: {trade['quantity']}股 @ ¥{trade['price']:.2f} (盈亏：¥{trade.get('pnl', 0):.2f})")
    
    # 生成周报告
    print("\n" + "="*70)
    print("📊 一周交易总结")
    print("="*70)
    
    final_value = account["daily_values"][-1]["total_value"]
    total_pnl = final_value - INITIAL_CAPITAL
    total_pnl_pct = total_pnl / INITIAL_CAPITAL * 100
    
    print(f"\n💰 初始资金：¥{INITIAL_CAPITAL:,.2f}")
    print(f"📈 最终总值：¥{final_value:,.2f}")
    print(f"💵 总盈亏：¥{total_pnl:,.2f} ({total_pnl_pct:+.2f}%)")
    print(f"📊 总交易：{sum(d['trades'] for d in account['daily_values'])} 笔")
    
    # 每日表现
    print("\n📅 每日表现:")
    print("-"*70)
    print(f"{'日期':<12} {'总值':<12} {'当日盈亏':<12} {'累计盈亏':<12} {'交易数':<8}")
    print("-"*70)
    
    for day in account["daily_values"]:
        print(f"{day['date']:<12} ¥{day['total_value']:>10,.2f} ¥{day['day_pnl']:>10,.2f} ¥{day['pnl']:>10,.2f} {day['trades']:>6}笔")
    
    # 保存报告
    report = {
        "period": f"{dates[0]} 至 {dates[-1]}",
        "initial_capital": INITIAL_CAPITAL,
        "final_value": final_value,
        "total_pnl": total_pnl,
        "total_pnl_pct": total_pnl_pct,
        "total_trades": sum(d['trades'] for d in account["daily_values"]),
        "daily_performance": account["daily_values"]
    }
    
    report_file = Path("/Users/kelvin/.openclaw/workspace/quant-trading-system/reports/week_simulation_report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 报告已保存：{report_file}")
    print("="*70)
    
    return report

if __name__ == "__main__":
    run_week_simulation()
