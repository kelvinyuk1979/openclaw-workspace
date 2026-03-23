#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polymarket 天气交易机器人 v1.0
基于 NWS 天气预报数据的 Polymarket 交易模拟系统

功能：
- 从 NWS（美国国家气象局）获取实时天气预报
- 通过 Gamma API 自动发现 Polymarket 天气市场
- 智能解析温度区间，寻找被低估的交易机会
- 模拟盘测试（10000 美元虚拟资金）

作者：AI Assistant
日期：2026-03-14
"""

import re
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime, timezone, timedelta import datetime, timezone, timedelta
from pathlib import Path


# 创建全局会话并配置重试机制 (最大重试3次，针对 50x 错误自动退避)
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))
session.mount('http://', HTTPAdapter(max_retries=retries))

# ==================== 配置部分 ====================


# 机场坐标 - 必须与 Polymarket 结算规则指定的观测点一致
LOCATIONS = {
    "nyc": {"lat": 40.7772, "lon": -73.8726, "name": "New York City (KLGA)"},
    "chicago": {"lat": 41.9742, "lon": -87.9073, "name": "Chicago (KORD)"},
    "miami": {"lat": 25.7959, "lon": -80.2870, "name": "Miami (KMIA)"},
    "dallas": {"lat": 32.8471, "lon": -96.8518, "name": "Dallas (KDAL)"},
    "seattle": {"lat": 47.4502, "lon": -122.3088, "name": "Seattle (KSEA)"},
    "atlanta": {"lat": 33.6407, "lon": -84.4277, "name": "Atlanta (KATL)"},
}

# NWS API 端点 - 每个城市对应的预报网格点
NWS_ENDPOINTS = {
    "nyc": "https://api.weather.gov/gridpoints/OKX/37,39/forecast/hourly",
    "chicago": "https://api.weather.gov/gridpoints/LOT/66,77/forecast/hourly",
    "miami": "https://api.weather.gov/gridpoints/MFL/106,51/forecast/hourly",
    "dallas": "https://api.weather.gov/gridpoints/FWD/87,107/forecast/hourly",
    "seattle": "https://api.weather.gov/gridpoints/SEW/124,61/forecast/hourly",
    "atlanta": "https://api.weather.gov/gridpoints/FFC/50,82/forecast/hourly",
}

# 气象站 ID - 用于获取实际观测数据
STATION_IDS = {
    "nyc": "KLGA", "chicago": "KORD", "miami": "KMIA",
    "dallas": "KDAL", "seattle": "KSEA", "atlanta": "KATL",
}

MONTHS = ["january", "february", "march", "april", "may", "june",
          "july", "august", "september", "october", "november", "december"]

# 交易策略参数（2026-03-14 调整）
ENTRY_THRESHOLD = 0.22      # 入场阈值：市场价格低于 22 美分（原 15¢，根据第 1 天数据调整）
EXIT_THRESHOLD = 0.50       # 出场阈值：价格达到 50 美分时卖出（原 45¢，给盈利更多空间）
POSITION_PCT = 0.03         # 单笔仓位：余额的 3%（原 5%，降低风险）
MAX_TRADES_PER_RUN = 5      # 每次运行最多交易笔数

# 模拟配置
SIM_FILE = "simulation.json"
SIM_BALANCE = 10000.0        # 初始虚拟资金

# ==================== 数据获取模块 ====================

def get_forecast(city_slug: str) -> dict:
    """
    获取天气预报数据
    
    策略：
    1. 先获取今天已过去的实际观测数据（避免遗漏已发生的最高温）
    2. 再获取未来几小时的预报数据
    3. 合并得到全天的最高温预报
    
    Args:
        city_slug: 城市标识符
        
    Returns:
        dict: 日期 -> 最高温度 (°F)
    """
    forecast_url = NWS_ENDPOINTS.get(city_slug)
    station_id = STATION_IDS.get(city_slug)
    daily_max = {}
    headers = {"User-Agent": "PolymarketWeatherBot/1.0"}
    
    # 1. 获取实际观测数据（今天已过去的时间）
    try:
        obs_url = f"https://api.weather.gov/stations/{station_id}/observations?limit=48"
        r = session.get(obs_url, timeout=10, headers=headers)
        r.raise_for_status()
        
        for obs in r.json().get("features", []):
            props = obs["properties"]
            time_str = props.get("timestamp", "")[:10]
            temp_c = props.get("temperature", {}).get("value")
            
            if temp_c is not None and time_str:
                temp_f = round(temp_c * 9/5 + 32)
                if time_str not in daily_max or temp_f > daily_max[time_str]:
                    daily_max[time_str] = temp_f
                    
    except Exception as e:
        print(f"  ⚠️  观测数据获取失败：{e}")
    
    # 2. 获取小时预报数据（未来时间）
    try:
        r = session.get(forecast_url, timeout=10, headers=headers)
        r.raise_for_status()
        periods = r.json()["properties"]["periods"]
        
        for p in periods:
            date = p["startTime"][:10]
            temp = p["temperature"]
            
            if p.get("temperatureUnit") == "C":
                temp = round(temp * 9/5 + 32)
            
            if date not in daily_max or temp > daily_max[date]:
                daily_max[date] = temp
                
    except Exception as e:
        print(f"  ⚠️  预报数据获取失败：{e}")
    
    return daily_max


def get_polymarket_event(city_slug: str, month: str, day: int, year: int) -> dict:
    """
    从 Polymarket Gamma API 获取天气市场信息
    
    Args:
        city_slug: 城市标识符
        month: 月份（英文小写）
        day: 日期
        year: 年份
        
    Returns:
        dict: 事件对象，包含所有市场和价格信息
    """
    slug = f"highest-temperature-in-{city_slug}-on-{month}-{day}-{year}"
    url = f"https://gamma-api.polymarket.com/events?slug={slug}"
    
    try:
        r = session.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        
        if data and isinstance(data, list) and len(data) > 0:
            return data[0]
    except Exception as e:
        print(f"  ⚠️  Polymarket API 错误：{e}")
    
    return None


def parse_temp_range(question: str) -> tuple:
    """
    解析温度区间问题
    
    将文字问题转换为数字区间：
    - "44-45°F" → (44, 45)
    - "48°F or higher" → (48, 999)
    - "40°F or below" → (-999, 40)
    
    Args:
        question: 市场问题文本
        
    Returns:
        tuple: (最低温，最高温)，无法解析返回 None
    """
    question_lower = question.lower()
    
    # "X°F or below"
    if "or below" in question_lower:
        m = re.search(r'(\d+)°F or below', question, re.IGNORECASE)
        if m:
            return (-999, int(m.group(1)))
    
    # "X°F or higher"
    if "or higher" in question_lower:
        m = re.search(r'(\d+)°F or higher', question, re.IGNORECASE)
        if m:
            return (int(m.group(1)), 999)
    
    # "between X-Y°F"
    m = re.search(r'between (\d+)-(\d+)°F', question, re.IGNORECASE)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    
    # "X-Y°F" (without "between")
    m = re.search(r'(\d+)-(\d+)°F', question, re.IGNORECASE)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    
    return None


# ==================== 模拟交易模块 ====================

def load_sim() -> dict:
    """加载模拟交易状态"""
    try:
        with open(SIM_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "balance": SIM_BALANCE,
            "starting_balance": SIM_BALANCE,
            "positions": {},
            "trades": [],
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "pending_positions": {},
        }


def save_sim(sim: dict):
    """保存模拟交易状态"""
    with open(SIM_FILE, 'w', encoding='utf-8') as f:
        json.dump(sim, f, indent=2, ensure_ascii=False)


def reset_sim():
    """重置模拟账户"""
    sim = {
        "balance": SIM_BALANCE,
        "starting_balance": SIM_BALANCE,
        "positions": {},
        "trades": [],
        "total_trades": 0,
        "wins": 0,
        "losses": 0,
        "pending_positions": {},
    }
    save_sim(sim)
    print(f"✅ 模拟账户已重置，初始资金：${SIM_BALANCE}")


def evaluate_position(position: dict, actual_temp: float = None) -> dict:
    """
    评估持仓结果
    
    Args:
        position: 持仓信息
        actual_temp: 实际结算温度（如果已知）
        
    Returns:
        dict: 评估结果
    """
    entry_price = position["entry_price"]
    shares = position["shares"]
    cost = position["cost"]
    
    # 如果已知实际温度，判断输赢
    if actual_temp is not None:
        rng = position["temp_range"]
        if rng[0] <= actual_temp <= rng[1]:
            # 赢了，获得 $1/share
            payout = shares * 1.0
            profit = payout - cost
            return {"result": "WIN", "payout": payout, "profit": profit}
        else:
            # 输了
            return {"result": "LOSS", "payout": 0, "profit": -cost}
    
    # 未知结果，返回当前状态
    return {"result": "PENDING", "payout": 0, "profit": 0}


# ==================== 主交易逻辑 ====================

def run(dry_run: bool = True, verbose: bool = True):
    """
    运行交易机器人
    
    Args:
        dry_run: True=仅显示信号不交易，False=执行模拟交易
        verbose: 是否输出详细信息
    """
    sim = load_sim()
    balance = sim["balance"]
    positions = sim.get("pending_positions", {})
    trades_executed = 0
    
    print("\n" + "="*60)
    print(f"🤖 Polymarket 天气交易机器人 v1.0")
    print(f"📅 运行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💰 当前余额：${balance:.2f}")
    print(f"📊 模式：{'模拟交易' if not dry_run else '观察模式'}")
    print("="*60 + "\n")
    
    signals_found = []
    
    for city_slug, city_info in LOCATIONS.items():
        if verbose:
            print(f"📍 分析：{city_info['name']}")
        
        # 获取天气预报
        forecast = get_forecast(city_slug)
        if not forecast:
            if verbose:
                print(f"  ⚠️  无法获取预报数据，跳过\n")
            continue
        
        # 分析未来 4 天
        for i in range(0, 4):
            date = datetime.now(timezone.utc) + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            month = MONTHS[date.month - 1]
            
            forecast_temp = forecast.get(date_str)
            if forecast_temp is None:
                continue
            
            # 获取 Polymarket 市场
            event = get_polymarket_event(city_slug, month, date.day, date.year)
            if not event:
                if verbose:
                    print(f"  📅 {date_str}: 无相关市场")
                continue
            
            if verbose:
                print(f"  📅 {date_str} | 预报最高温：{forecast_temp}°F")
            
            # 分析每个市场
            for market in event.get("markets", []):
                question = market.get("question", "")
                rng = parse_temp_range(question)
                
                if not rng:
                    continue
                
                # 检查预报温度是否在该区间内
                if rng[0] <= forecast_temp <= rng[1]:
                    try:
                        prices = json.loads(market.get("outcomePrices", "[0.5,0.5]"))
                        yes_price = float(prices[0])
                    except Exception:
                        continue
                    
                    signal_info = {
                        "city": city_info['name'],
                        "date": date_str,
                        "forecast_temp": forecast_temp,
                        "question": question[:60],
                        "price": yes_price,
                        "range": rng,
                    }
                    signals_found.append(signal_info)
                    
                    if verbose:
                        print(f"    🎯 匹配区间：{question[:50]}...")
                        print(f"       价格：${yes_price:.3f}")
                    
                    # 检查是否满足入场条件
                    if yes_price < ENTRY_THRESHOLD:
                        market_id = market.get("id", "")
                        position_size = round(balance * POSITION_PCT, 2)
                        shares = position_size / yes_price if yes_price > 0 else 0
                        
                        if verbose:
                            print(f"    ✅ 交易信号！")
                            print(f"       建议买入：{shares:.1f} 股 @ ${yes_price:.3f}")
                            print(f"       仓位金额：${position_size:.2f}")
                            print(f"       预期回报：${shares:.1f} (如果命中)")
                        
                        if not dry_run and market_id not in positions and trades_executed < MAX_TRADES_PER_RUN:
                            # 执行模拟交易
                            balance -= position_size
                            positions[market_id] = {
                                "question": question,
                                "entry_price": yes_price,
                                "shares": shares,
                                "cost": position_size,
                                "date": date_str,
                                "location": city_slug,
                                "forecast_temp": forecast_temp,
                                "temp_range": rng,
                                "opened_at": datetime.now().isoformat(),
                            }
                            trades_executed += 1
                            
                            sim["total_trades"] += 1
                            sim["trades"].append({
                                "type": "BUY",
                                "market_id": market_id,
                                "city": city_info['name'],
                                "date": date_str,
                                "question": question[:80],
                                "shares": shares,
                                "entry_price": yes_price,
                                "cost": position_size,
                                "forecast_temp": forecast_temp,
                                "timestamp": datetime.now().isoformat(),
                            })
                            
                            if verbose:
                                print(f"    📝 已记录模拟持仓\n")
                            break
            
            if verbose:
                print()
    
    # 保存模拟状态
    sim["balance"] = round(balance, 2)
    sim["pending_positions"] = positions
    sim["last_run"] = datetime.now().isoformat()
    save_sim(sim)
    
    # 输出汇总报告
    print("\n" + "="*60)
    print("📊 运行汇总")
    print("="*60)
    print(f"💰 余额：${balance:.2f} (初始：${sim['starting_balance']:.2f})")
    print(f"📈 总交易数：{sim['total_trades']}")
    print(f"📝 本次发现信号：{len(signals_found)}")
    print(f"✅ 本次执行交易：{trades_executed}")
    print(f"📂 当前持仓：{len(positions)}")
    print("="*60)
    
    # 生成信号报告
    if signals_found:
        print("\n📋 发现的交易信号:")
        for i, sig in enumerate(signals_found[:10], 1):
            print(f"  {i}. {sig['city']} - {sig['date']}")
            print(f"     预报：{sig['forecast_temp']}°F | 价格：${sig['price']:.3f}")
            print(f"     区间：{sig['question'][:40]}...")
    
    return {
        "balance": balance,
        "signals": signals_found,
        "trades_executed": trades_executed,
        "positions": positions,
    }


def generate_report():
    """生成模拟交易报告"""
    sim = load_sim()
    
    print("\n" + "="*70)
    print("📈 Polymarket 天气交易机器人 - 模拟交易报告")
    print("="*70)
    print(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 账户概览
    print("💰 账户概览")
    print("-"*40)
    print(f"初始资金：     ${sim['starting_balance']:.2f}")
    print(f"当前余额：     ${sim['balance']:.2f}")
    print(f"总盈亏：       ${sim['balance'] - sim['starting_balance']:+.2f}")
    print(f"收益率：       {(sim['balance'] / sim['starting_balance'] - 1) * 100:+.2f}%")
    print()
    
    # 交易统计
    print("📊 交易统计")
    print("-"*40)
    print(f"总交易数：     {sim['total_trades']}")
    print(f"获胜：         {sim.get('wins', 0)}")
    print(f"失败：         {sim.get('losses', 0)}")
    if sim.get('wins', 0) + sim.get('losses', 0) > 0:
        win_rate = sim.get('wins', 0) / (sim.get('wins', 0) + sim.get('losses', 0)) * 100
        print(f"胜率：         {win_rate:.1f}%")
    print()
    
    # 当前持仓
    if sim.get('pending_positions'):
        print("📂 当前持仓")
        print("-"*40)
        for mid, pos in sim['pending_positions'].items():
            print(f"📍 {pos['location']} - {pos['date']}")
            print(f"   问题：{pos['question'][:60]}...")
            print(f"   预报温度：{pos['forecast_temp']}°F")
            print(f"   入场价格：${pos['entry_price']:.3f}")
            print(f"   持仓数量：{pos['shares']:.1f} 股")
            print(f"   成本：    ${pos['cost']:.2f}")
            print()
    
    # 最近交易记录
    if sim.get('trades'):
        print("📜 最近交易记录")
        print("-"*40)
        for trade in sim['trades'][-10:]:
            print(f"{trade['timestamp'][:10]} | {trade['city'][:15]} | "
                  f"{'BUY':5} | ${trade['cost']:.2f} | {trade['question'][:40]}...")
    
    print("\n" + "="*70)
    
    # 保存到文件
    report_file = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"# Polymarket 天气交易机器人 - 模拟交易报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## 账户概览\n\n")
        f.write(f"- 初始资金：${sim['starting_balance']:.2f}\n")
        f.write(f"- 当前余额：${sim['balance']:.2f}\n")
        f.write(f"- 总盈亏：${sim['balance'] - sim['starting_balance']:+.2f}\n")
        f.write(f"- 收益率：{(sim['balance'] / sim['starting_balance'] - 1) * 100:+.2f}%\n\n")
        f.write(f"## 交易统计\n\n")
        f.write(f"- 总交易数：{sim['total_trades']}\n")
        f.write(f"- 获胜：{sim.get('wins', 0)}\n")
        f.write(f"- 失败：{sim.get('losses', 0)}\n")
    
    print(f"📄 报告已保存：{report_file}")
    return sim


# ==================== 命令行入口 ====================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Polymarket 天气交易机器人")
    parser.add_argument("--live", action="store_true", help="执行模拟交易（默认仅观察）")
    parser.add_argument("--reset", action="store_true", help="重置模拟账户")
    parser.add_argument("--report", action="store_true", help="生成交易报告")
    parser.add_argument("--quiet", action="store_true", help="减少输出信息")
    args = parser.parse_args()
    
    if args.reset:
        reset_sim()
    elif args.report:
        generate_report()
    else:
        run(dry_run=not args.live, verbose=not args.quiet)
