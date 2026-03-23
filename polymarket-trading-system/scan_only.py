#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polymarket 统一交易系统 - 仅扫描（不发送邮件）
用于高频扫描，每 15 分钟运行一次
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


def log(message: str):
    """写入日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {message}\n"
    print(log_line, end='')
    
    # 追加到日志文件
    with open(LOG_DIR / 'scan.log', 'a', encoding='utf-8') as f:
        f.write(log_line)


def run_scan():
    """执行扫描"""
    config = load_config()
    results = {}
    
    # 只运行启用的策略
    if config['strategies']['quant_core']['enabled']:
        log("📊 扫描量化核心策略...")
        try:
            sys.path.insert(0, str(SCRIPT_DIR / 'strategies' / 'quant_core'))
            from adapter import run as quant_run
            results['quant'] = quant_run()
            log(f"  ✅ {len(results['quant'].get('signals', []))} 个信号")
        except Exception as e:
            log(f"  ⚠️ 跳过：{e}")
            results['quant'] = {"signals": [], "error": str(e)}
    
    if config['strategies']['weather_arb']['enabled']:
        log("🌤️ 扫描天气套利策略...")
        try:
            sys.path.insert(0, str(SCRIPT_DIR / 'strategies' / 'weather_arb'))
            from adapter import run as weather_run
            results['weather'] = weather_run()
            log(f"  ✅ {len(results['weather'].get('signals', []))} 个信号")
        except Exception as e:
            log(f"  ⚠️ 跳过：{e}")
            results['weather'] = {"signals": [], "error": str(e)}
    
    if config['strategies']['event_trading']['enabled']:
        log("📅 扫描事件交易策略...")
        try:
            sys.path.insert(0, str(SCRIPT_DIR / 'strategies' / 'event_trading'))
            from adapter import run as event_run
            results['event'] = event_run()
            log(f"  ✅ {len(results['event'].get('signals', []))} 个信号")
        except Exception as e:
            log(f"  ⚠️ 跳过：{e}")
            results['event'] = {"signals": [], "error": str(e)}
    
    # 保存扫描结果（供邮件报告读取）
    scan_data = {
        "last_scan": datetime.now().isoformat(),
        "results": results
    }
    
    scan_file = LOG_DIR / 'latest_scan.json'
    with open(scan_file, 'w', encoding='utf-8') as f:
        json.dump(scan_data, f, ensure_ascii=False, indent=2)
    
    log(f"📄 扫描结果已保存：{scan_file}")
    return results


if __name__ == "__main__":
    log("=" * 50)
    log("🔍 Polymarket 扫描开始")
    log("=" * 50)
    run_scan()
    log("=" * 50)
    log("✅ 扫描完成")
    log("=" * 50)
