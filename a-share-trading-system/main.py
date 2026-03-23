#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股统一交易系统 - 主入口
整合：技术面 + 基本面 + 情绪面 三策略
"""

import json
import sys
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / 'config' / 'unified_config.json'
LOG_DIR = SCRIPT_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)


def load_config():
    """加载配置"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_latest_scan() -> dict:
    """读取最新扫描结果"""
    scan_file = LOG_DIR / 'latest_scan.json'
    if scan_file.exists():
        with open(scan_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def run_technical(config: dict) -> dict:
    """运行技术面策略"""
    print("\n📊 运行技术面策略...")
    
    scan_data = load_latest_scan()
    if scan_data and 'technical' in scan_data.get('results', {}):
        result = scan_data['results']['technical']
        print(f"✅ 技术面完成（读取扫描） - {len(result.get('signals', []))} 个信号")
        return result
    
    try:
        sys.path.insert(0, str(SCRIPT_DIR / 'strategies' / 'technical'))
        from adapter import run as tech_run
        result = tech_run(config.get('strategies', {}).get('technical', {}).get('config', {}))
        print(f"✅ 技术面完成 - {len(result.get('signals', []))} 个信号")
        return result
    except Exception as e:
        print(f"⚠️ 技术面跳过：{e}")
    return {"signals": [], "trades": 0, "pnl": 0.0}


def run_fundamental(config: dict) -> dict:
    """运行基本面策略"""
    print("\n💰 运行基本面策略...")
    
    scan_data = load_latest_scan()
    if scan_data and 'fundamental' in scan_data.get('results', {}):
        result = scan_data['results']['fundamental']
        print(f"✅ 基本面完成（读取扫描） - {len(result.get('signals', []))} 个信号")
        return result
    
    try:
        sys.path.insert(0, str(SCRIPT_DIR / 'strategies' / 'fundamental'))
        from adapter import run as fund_run
        result = fund_run(config.get('strategies', {}).get('fundamental', {}).get('config', {}))
        print(f"✅ 基本面完成 - {len(result.get('signals', []))} 个信号")
        return result
    except Exception as e:
        print(f"⚠️ 基本面跳过：{e}")
    return {"signals": [], "trades": 0, "pnl": 0.0}


def run_sentiment(config: dict) -> dict:
    """运行情绪面策略"""
    print("\n📈 运行情绪面策略...")
    
    scan_data = load_latest_scan()
    if scan_data and 'sentiment' in scan_data.get('results', {}):
        result = scan_data['results']['sentiment']
        print(f"✅ 情绪面完成（读取扫描） - {len(result.get('signals', []))} 个信号")
        return result
    
    try:
        sys.path.insert(0, str(SCRIPT_DIR / 'strategies' / 'sentiment'))
        from adapter import run as sent_run
        result = sent_run(config.get('strategies', {}).get('sentiment', {}).get('config', {}))
        print(f"✅ 情绪面完成 - {len(result.get('signals', []))} 个信号")
        return result
    except Exception as e:
        print(f"⚠️ 情绪面跳过：{e}")
    return {"signals": [], "trades": 0, "pnl": 0.0}


def send_report(technical: dict, fundamental: dict, sentiment: dict, config: dict):
    """发送统一邮件报告"""
    print("\n📧 生成统一报告...")
    try:
        from reports.daily_report import generate_and_send
        generate_and_send(technical, fundamental, sentiment, config)
        print("✅ 报告已发送")
    except Exception as e:
        print(f"⚠️ 报告发送失败：{e}")
        from reports.daily_report import save_draft
        save_draft(technical, fundamental, sentiment, config)
        print("📄 报告已保存到 drafts/")


def main():
    """主函数"""
    print("=" * 60)
    print(f"📈 A 股统一交易系统")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    config = load_config()
    
    # 运行各策略
    technical_result = run_technical(config) if config['strategies']['technical']['enabled'] else {}
    fundamental_result = run_fundamental(config) if config['strategies']['fundamental']['enabled'] else {}
    sentiment_result = run_sentiment(config) if config['strategies']['sentiment']['enabled'] else {}
    
    # 发送统一报告
    if config.get('email', {}).get('enabled'):
        send_report(technical_result, fundamental_result, sentiment_result, config)
    
    print("\n" + "=" * 60)
    print("✅ 所有策略运行完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
