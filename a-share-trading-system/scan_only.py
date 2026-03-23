#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股统一交易系统 - 仅扫描（不发送邮件）
用于高频扫描，每 30 分钟运行一次
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
    
    with open(LOG_DIR / 'scan.log', 'a', encoding='utf-8') as f:
        f.write(log_line)


def run_scan():
    """执行扫描"""
    config = load_config()
    results = {}
    
    if config['strategies']['technical']['enabled']:
        log("📊 扫描技术面策略...")
        try:
            sys.path.insert(0, str(SCRIPT_DIR / 'strategies' / 'technical'))
            from adapter import run as tech_run
            results['technical'] = tech_run()
            log(f"  ✅ {len(results['technical'].get('signals', []))} 个信号")
        except Exception as e:
            log(f"  ⚠️ 跳过：{e}")
            results['technical'] = {"signals": [], "error": str(e)}
    
    if config['strategies']['fundamental']['enabled']:
        log("💰 扫描基本面策略...")
        try:
            sys.path.insert(0, str(SCRIPT_DIR / 'strategies' / 'fundamental'))
            from adapter import run as fund_run
            results['fundamental'] = fund_run()
            log(f"  ✅ {len(results['fundamental'].get('signals', []))} 个信号")
        except Exception as e:
            log(f"  ⚠️ 跳过：{e}")
            results['fundamental'] = {"signals": [], "error": str(e)}
    
    if config['strategies']['sentiment']['enabled']:
        log("📈 扫描情绪面策略...")
        try:
            sys.path.insert(0, str(SCRIPT_DIR / 'strategies' / 'sentiment'))
            from adapter import run as sent_run
            results['sentiment'] = sent_run()
            log(f"  ✅ {len(results['sentiment'].get('signals', []))} 个信号")
        except Exception as e:
            log(f"  ⚠️ 跳过：{e}")
            results['sentiment'] = {"signals": [], "error": str(e)}
    
    # 保存扫描结果
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
    log("🔍 A 股扫描开始")
    log("=" * 50)
    run_scan()
    log("=" * 50)
    log("✅ 扫描完成")
    log("=" * 50)
