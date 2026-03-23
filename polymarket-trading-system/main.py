#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polymarket 统一交易系统
整合：quant-core + weather-arb + event-trading
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / 'config' / 'unified_config.json'


def load_config():
    """加载统一配置"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_latest_scan() -> dict:
    """读取最新扫描结果（由 scan_only.py 生成）"""
    scan_file = SCRIPT_DIR / 'logs' / 'latest_scan.json'
    if scan_file.exists():
        with open(scan_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def run_quant_core(config: dict) -> dict:
    """运行量化核心策略（或读取扫描结果）"""
    print("\n📊 运行量化核心策略...")
    
    # 优先读取扫描结果
    scan_data = load_latest_scan()
    if scan_data and 'quant' in scan_data.get('results', {}):
        result = scan_data['results']['quant']
        print(f"✅ 量化核心完成（读取扫描） - {len(result.get('signals', []))} 个信号")
        return result
    
    # 否则实时运行
    try:
        quant_dir = SCRIPT_DIR / 'strategies' / 'quant_core'
        sys.path.insert(0, str(quant_dir))
        from adapter import run as quant_run
        result = quant_run(config.get('strategies', {}).get('quant_core', {}).get('config', {}))
        print(f"✅ 量化核心完成 - {len(result.get('signals', []))} 个信号")
        return result
    except Exception as e:
        print(f"⚠️ 量化核心跳过：{e}")
    return {"signals": [], "trades": 0, "pnl": 0.0}


def run_weather_arb(config: dict) -> dict:
    """运行天气套利策略（或读取扫描结果）"""
    print("\n🌤️ 运行天气套利策略...")
    
    # 优先读取扫描结果
    scan_data = load_latest_scan()
    if scan_data and 'weather' in scan_data.get('results', {}):
        result = scan_data['results']['weather']
        print(f"✅ 天气套利完成（读取扫描） - {len(result.get('signals', []))} 个信号")
        return result
    
    # 否则实时运行
    try:
        weather_dir = SCRIPT_DIR / 'strategies' / 'weather_arb'
        sys.path.insert(0, str(weather_dir))
        from adapter import run as weather_run
        result = weather_run(config.get('strategies', {}).get('weather_arb', {}).get('config', {}))
        print(f"✅ 天气套利完成 - {len(result.get('signals', []))} 个信号")
        return result
    except Exception as e:
        print(f"⚠️ 天气套利跳过：{e}")
    return {"signals": [], "trades": 0, "pnl": 0.0}


def run_event_trading(config: dict) -> dict:
    """运行事件交易策略（或读取扫描结果）"""
    print("\n📅 运行事件交易策略...")
    
    # 优先读取扫描结果
    scan_data = load_latest_scan()
    if scan_data and 'event' in scan_data.get('results', {}):
        result = scan_data['results']['event']
        print(f"✅ 事件交易完成（读取扫描） - {len(result.get('signals', []))} 个信号")
        return result
    
    # 否则实时运行
    try:
        event_dir = SCRIPT_DIR / 'strategies' / 'event_trading'
        sys.path.insert(0, str(event_dir))
        from adapter import run as event_run
        result = event_run(config.get('strategies', {}).get('event_trading', {}).get('config', {}))
        print(f"✅ 事件交易完成 - {len(result.get('signals', []))} 个信号")
        return result
    except Exception as e:
        print(f"⚠️ 事件交易跳过：{e}")
    return {"signals": [], "trades": 0, "pnl": 0.0}


def send_unified_report(quant_result: dict, weather_result: dict, event_result: dict, config: dict):
    """发送统一邮件报告"""
    print("\n📧 生成统一报告...")
    try:
        from reports.daily_report import generate_and_send
        generate_and_send(quant_result, weather_result, event_result, config)
        print("✅ 报告已发送")
    except Exception as e:
        print(f"⚠️ 报告发送失败：{e}")
        from reports.daily_report import save_draft
        save_draft(quant_result, weather_result, event_result, config)
        print("📄 报告已保存到 drafts/")


def main():
    """主函数"""
    print("=" * 60)
    print(f"🤖 Polymarket 统一交易系统")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    config = load_config()
    
    # 运行各策略
    quant_result = run_quant_core(config) if config['strategies']['quant_core']['enabled'] else {}
    weather_result = run_weather_arb(config) if config['strategies']['weather_arb']['enabled'] else {}
    event_result = run_event_trading(config) if config['strategies']['event_trading']['enabled'] else {}
    
    # 发送统一报告
    if config.get('email', {}).get('enabled'):
        send_unified_report(quant_result, weather_result, event_result, config)
    
    print("\n" + "=" * 60)
    print("✅ 所有策略运行完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
