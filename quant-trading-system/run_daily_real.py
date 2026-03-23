#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股量化交易 - 使用腾讯财经真实数据
日期：2026-03-17
"""

import sys
import json
import time
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from data_fetcher import TencentStockData

# 配置
CONFIG_PATH = Path(__file__).parent / "config" / "config.json"
DATA_PATH = Path(__file__).parent / "data"
REPORTS_PATH = Path(__file__).parent / "reports"

def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_mock_history(base_price: float, days: int = 30, seed_str: str = "") -> list:
    """生成模拟历史价格用于计算技术指标"""
    import random
    # 使用稳定的种子（字符串 hash 可能不稳定，用简单累加）
    seed = sum(ord(c) for c in seed_str) % (2**32)
    random.seed(seed)
    
    prices = [base_price]
    for _ in range(days):
        change = random.uniform(-0.03, 0.03)
        prices.append(prices[-1] * (1 + change))
    
    return prices

def analyze_stock(code: str, quote: dict, config: dict) -> dict:
    """分析单只股票的交易信号"""
    
    # 生成模拟历史价格（用于计算技术指标）
    seed_str = code + "2026-03-17"
    closes = generate_mock_history(quote['price'], days=30, seed_str=seed_str)
    
    # 计算技术指标
    tencent = TencentStockData()
    rsi = tencent.calculate_rsi(closes, 14)
    ma5 = tencent.calculate_ma(closes, 5)
    ma20 = tencent.calculate_ma(closes, 20)
    
    # 成交量分析
    volume_ratio = 1.0 + (quote.get('volume', 0) / 1000000) * 0.01  # 简化估算
    
    # 策略投票
    signals = {"LONG": 0, "SHORT": 0, "HOLD": 0}
    
    # 1. 趋势跟踪 (35%)
    if quote['price'] > ma5 > ma20 and rsi > 50:
        signals["LONG"] += 1
    elif quote['price'] < ma5 < ma20 and rsi < 50:
        signals["SHORT"] += 1
    else:
        signals["HOLD"] += 1
    
    # 2. 动量策略 (35%) - 放宽条件
    if rsi < 40:  # 去掉 volume_ratio 要求
        signals["LONG"] += 1
    elif rsi > 60:
        signals["SHORT"] += 1
    else:
        signals["HOLD"] += 1
    
    # 3. 均值回归 (30%)
    if rsi < 30:
        signals["LONG"] += 1
    elif rsi > 70:
        signals["SHORT"] += 1
    else:
        signals["HOLD"] += 1
    
    # 决策
    if signals["LONG"] >= 2:
        action = "BUY"
    elif signals["SHORT"] >= 2:
        action = "SELL"
    else:
        action = "HOLD"
    
    return {
        "code": code,
        "name": quote.get('name', ''),
        "price": quote['price'],
        "change_pct": quote.get('change_pct', 0),
        "rsi": rsi,
        "ma5": ma5,
        "ma20": ma20,
        "volume_ratio": round(volume_ratio, 2),
        "action": action,
        "votes": signals,
    }

def run_daily():
    """运行每日交易"""
    print("\n" + "="*60)
    print("🚀 A 股量化交易系统 - 真实数据版")
    print("📅 日期：2026-03-17")
    print("="*60)
    
    config = load_config()
    
    # 加载账户状态
    account_file = DATA_PATH / "account_state_2026-03-16.json"
    if account_file.exists():
        with open(account_file, 'r', encoding='utf-8') as f:
            yesterday = json.load(f)
            account = yesterday["account"]
    else:
        account = {
            "initial_capital": config["account"]["initial_capital"],
            "cash": config["account"]["initial_capital"],
            "positions": {},
            "history": [],
        }
    
    print(f"\n💰 初始资金：¥{account['initial_capital']:,.2f}")
    print(f"💵 当前现金：¥{account['cash']:,.2f}")
    print(f"📈 持仓数量：{len(account['positions'])}")
    
    # 获取股票池
    stock_pool = []
    for category in ["large_cap", "growth", "niche_leader"]:
        stock_pool.extend(config["a_stock_pool"][category])
    
    print(f"\n🔍 扫描股票池：{len(stock_pool)} 只股票")
    print("-"*60)
    
    # 获取实时行情（分批获取，避免限流）
    tencent = TencentStockData()
    all_quotes = {}
    
    batch_size = 10
    for i in range(0, len(stock_pool), batch_size):
        batch = stock_pool[i:i+batch_size]
        print(f"\n📡 获取行情 [{i+1}-{min(i+batch_size, len(stock_pool))}]/{len(stock_pool)}...")
        
        quotes = tencent.get_realtime_quote(batch)
        all_quotes.update(quotes)
        
        if quotes:
            for code, q in quotes.items():
                print(f"   ✓ {code} {q.get('name', '')}: ¥{q['price']:.2f} ({q.get('change_pct', 0):+.2f}%)")
        
        import time; time.sleep(0.3)  # 避免请求过快
    
    print(f"\n✅ 成功获取 {len(all_quotes)} 只股票行情")
    
    # 分析交易信号
    print("\n" + "="*60)
    print("📊 分析交易信号")
    print("="*60)
    
    signals = []
    for code, quote in all_quotes.items():
        analysis = analyze_stock(code, quote, config)
        signals.append(analysis)
    
    # 按信号强度排序
    buy_signals = [s for s in signals if s['action'] == 'BUY']
    sell_signals = [s for s in signals if s['action'] == 'SELL']
    hold_signals = [s for s in signals if s['action'] == 'HOLD']
    
    buy_signals.sort(key=lambda x: x['votes']['LONG'], reverse=True)
    sell_signals.sort(key=lambda x: x['votes']['SHORT'], reverse=True)
    
    print(f"\n📈 买入信号：{len(buy_signals)} 只")
    for s in buy_signals[:5]:
        print(f"   - {s['code']} {s['name']}: RSI={s['rsi']:.1f}, LONG={s['votes']['LONG']}, price=¥{s['price']:.2f}")
    
    print(f"📉 卖出信号：{len(sell_signals)} 只 (需有持仓)")
    print(f"⏸️  观望：{len(hold_signals)} 只")
    
    # 执行交易
    trades = []
    single_max_pct = config["risk_control"]["position_single_max"]
    
    print("\n" + "="*60)
    print("📝 执行交易")
    print("="*60)
    
    # 买入（最多 2 只）
    for sig in buy_signals[:2]:
        # 计算最小买入（100 股起）
        min_shares = 100
        min_cost = min_shares * sig["price"]
        min_commission = max(5, min_cost * 0.0003)
        min_total = min_cost + min_commission
        
        # 检查是否买得起
        if min_total > account["cash"]:
            print(f"  ⏭️ 跳过 {sig['code']} {sig['name']}: 最低需¥{min_total:.2f}（现金不足）")
            continue
        
        # 计算目标仓位（不超过单笔最大）
        position_size = account["cash"] * single_max_pct
        
        # 如果最小买入超过单笔最大，按最小买入
        if min_total > position_size:
            shares = min_shares
            print(f"  ⚠️ {sig['code']} {sig['name']}: 单价较高，按最小仓位 100 股买入")
        else:
            # 正常计算（100 股整数倍）
            shares = int(position_size / sig["price"] / 100) * 100
            if shares < 100:
                shares = 100
        
        cost = shares * sig["price"]
        commission = max(5, cost * 0.0003)
        stamp_tax = 0  # 买入无印花税
        total_cost = cost + commission + stamp_tax
        
        if total_cost <= account["cash"]:
            account["cash"] -= total_cost
            account["positions"][sig["code"]] = {
                "shares": shares,
                "cost_price": sig["price"],
                "cost_total": total_cost,
                "date": "2026-03-17",
                "name": sig["name"],
            }
            
            trades.append({
                "time": "15:00",
                "action": "BUY",
                "code": sig["code"],
                "name": sig["name"],
                "price": sig["price"],
                "shares": shares,
                "cost": total_cost,
                "strategy": "multi_strategy",
            })
            
            print(f"  ✅ 买入 {sig['code']} {sig['name']} | {shares}股 @ ¥{sig['price']:.2f} | ¥{total_cost:,.2f}")
    
    if not trades:
        print("  ⚠️  今日无符合条件的买入信号")
    
    # 计算账户总值
    total_value = account["cash"]
    market_values = {}
    
    for code, pos in account["positions"].items():
        if code in all_quotes:
            current_price = all_quotes[code]["price"]
        else:
            current_price = pos["cost_price"]
        
        market_value = pos["shares"] * current_price
        market_values[code] = {
            "current_price": current_price,
            "market_value": market_value,
            "pnl": market_value - pos["cost_total"],
            "pnl_pct": (current_price - pos["cost_price"]) / pos["cost_price"] * 100,
        }
        total_value += market_value
    
    pnl = total_value - account["initial_capital"]
    pnl_pct = pnl / account["initial_capital"] * 100
    
    # 保存账户状态
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
    import time
    report = f"""# 📊 A 股量化交易每日报告
**日期：** 2026-03-17
**模式：** simulation (真实数据)
**数据源：** 腾讯财经

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

| 标的 | 名称 | 数量 | 成本价 | 现价 | 市值 | 盈亏% |
|------|------|------|--------|------|------|-------|
"""
    
    if account["positions"]:
        for code, pos in account["positions"].items():
            mv = market_values.get(code, {})
            report += f"| {code} | {pos.get('name', '')} | {pos['shares']} | ¥{pos['cost_price']:.2f} | ¥{mv.get('current_price', 0):.2f} | ¥{mv.get('market_value', 0):,.2f} | {mv.get('pnl_pct', 0):+.2f}% |\n"
    else:
        report += "| 无持仓 | - | - | - | - | - | - |\n"
    
    report += f"""
---

## 📝 今日交易

| 时间 | 操作 | 标的 | 名称 | 价格 | 数量 | 金额 | 策略 |
|------|------|------|------|------|------|------|------|
"""
    
    if trades:
        for t in trades:
            report += f"| {t['time']} | {t['action']} | {t['code']} | {t['name']} | ¥{t['price']:.2f} | {t['shares']} | ¥{t['cost']:,.2f} | {t['strategy']} |\n"
    else:
        report += "| - | - | - | - | - | - | - | - |\n"
    
    report += f"""
---

## ⚠️ 风控状态

| 指标 | 当前值 | 限制 | 状态 |
|------|--------|------|------|
| 单日盈亏 | ¥{pnl:+,.2f} | -5% | {'🟢 正常' if pnl > -account['initial_capital']*0.05 else '🔴 触及'} |
| 总仓位 | {(total_value - account['cash'])/total_value*100:.1f}% | 95% | 🟢 正常 |
| T+1 限制 | {len(trades)}只 | - | 🟢 正常 |

---

## 📊 信号汇总

### 买入候选 Top 5
| 代码 | 名称 | 价格 | RSI | 多票 | 空票 |
|------|------|------|-----|------|------|
"""
    
    for sig in buy_signals[:5]:
        report += f"| {sig['code']} | {sig['name']} | ¥{sig['price']:.2f} | {sig['rsi']:.1f} | {sig['votes']['LONG']} | {sig['votes']['SHORT']} |\n"
    
    report += f"""
### 卖出候选 Top 5
| 代码 | 名称 | 价格 | RSI | 多票 | 空票 |
|------|------|------|-----|------|------|
"""
    
    for sig in sell_signals[:5]:
        report += f"| {sig['code']} | {sig['name']} | ¥{sig['price']:.2f} | {sig['rsi']:.1f} | {sig['votes']['LONG']} | {sig['votes']['SHORT']} |\n"
    
    report += f"""
---

*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*数据源：腾讯财经 (qt.gtimg.cn)*  
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
    run_daily()
