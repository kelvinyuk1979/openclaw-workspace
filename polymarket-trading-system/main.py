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


def write_to_memory(result: dict, config: dict):
    """写入记忆文件"""
    if not config.get('logging', {}).get('write_memory'):
        return
    
    today = datetime.now().strftime('%Y-%m-%d')
    memory_file = Path.home() / '.openclaw' / 'workspace' / 'memory' / f'{today}.md'
    memory_file.parent.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    total_pnl = result.get('total_pnl', 0)
    total_trades = result.get('total_trades', 0)
    
    content = f"\n### 🎲 Polymarket 自动交易 ({timestamp})\n\n"
    content += f"- **总盈亏**: {total_pnl:.2f} USDC\n"
    content += f"- **交易数**: {total_trades}\n"
    content += f"- **运行模式**: {config.get('mode', 'live')}\n\n"
    
    with open(memory_file, 'a', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 已写入记忆文件：{memory_file}")


def git_commit(result: dict):
    """Git 提交交易记录"""
    try:
        workspace = Path.home() / '.openclaw' / 'workspace'
        subprocess.run(['git', 'add', '-A'], cwd=workspace, capture_output=True)
        subprocess.run(['git', 'commit', '-m', f'Polymarket 自动交易：{result.get("total_trades", 0)} 笔交易，盈亏 {result.get("total_pnl", 0):.2f} USDC'], 
                      cwd=workspace, capture_output=True)
        print("✅ Git 提交成功")
    except Exception as e:
        print(f"⚠️ Git 提交失败：{e}")


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


def execute_auto_trades(quant_result: dict, weather_result: dict, event_result: dict, config: dict) -> dict:
    """执行自动交易"""
    if config.get('mode') != 'live':
        print("ℹ️ 模拟模式，不执行实盘交易")
        return {"trades_executed": 0, "pnl": 0.0}
    
    print("\n💰 执行自动交易...")
    total_trades = 0
    total_pnl = 0.0
    
    # 执行量化核心交易
    for strategy_name, result in [('quant', quant_result), ('weather', weather_result), ('event', event_result)]:
        auto_exec = config.get('strategies', {}).get(f'{strategy_name}_core' if strategy_name == 'quant' else f'{strategy_name}_arb' if strategy_name == 'weather' else f'{strategy_name}_trading', {}).get('auto_execute', False)
        if auto_exec and result.get('signals'):
            for signal in result['signals']:
                confidence = signal.get('confidence', 0)
                if isinstance(confidence, str):
                    confidence = float(confidence) if confidence.replace('.', '').isdigit() else 0
                if signal.get('action') == 'BUY' and confidence >= 0.60:
                    print(f"  📈 买入：{signal.get('market', 'Unknown')} @ {signal.get('price', 'N/A')}")
                    total_trades += 1
                    # 实际 API 调用在此添加
    
    print(f"✅ 执行完成：{total_trades} 笔交易")
    return {"trades_executed": total_trades, "pnl": total_pnl}


def main():
    """主函数"""
    print("=" * 60)
    print(f"🤖 Polymarket 统一交易系统")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    config = load_config()
    print(f"📌 运行模式：{config.get('mode', 'simulation')}")
    print(f"📌 自动执行：{'✅ 启用' if config.get('mode') == 'live' else '❌ 禁用'}")
    
    # 运行各策略
    quant_result = run_quant_core(config) if config['strategies']['quant_core']['enabled'] else {}
    weather_result = run_weather_arb(config) if config['strategies']['weather_arb']['enabled'] else {}
    event_result = run_event_trading(config) if config['strategies']['event_trading']['enabled'] else {}
    
    # 汇总结果
    total_trades = (len(quant_result.get('signals', [])) + 
                   len(weather_result.get('signals', [])) + 
                   len(event_result.get('signals', [])))
    total_pnl = (quant_result.get('pnl', 0) + 
                weather_result.get('pnl', 0) + 
                event_result.get('pnl', 0))
    
    # 执行自动交易
    if config.get('mode') == 'live':
        exec_result = execute_auto_trades(quant_result, weather_result, event_result, config)
        total_trades = exec_result.get('trades_executed', total_trades)
        total_pnl = exec_result.get('pnl', total_pnl)
    
    # 写入记忆
    result_summary = {
        'total_trades': total_trades,
        'total_pnl': total_pnl,
        'quant_signals': len(quant_result.get('signals', [])),
        'weather_signals': len(weather_result.get('signals', [])),
        'event_signals': len(event_result.get('signals', []))
    }
    write_to_memory(result_summary, config)
    
    # Git 提交
    if config.get('logging', {}).get('git_commit'):
        git_commit(result_summary)
    
    # 发送统一报告
    if config.get('email', {}).get('enabled'):
        send_unified_report(quant_result, weather_result, event_result, config)
    
    print("\n" + "=" * 60)
    print(f"✅ 所有策略运行完成")
    print(f"📊 总信号：{total_trades} | 总盈亏：{total_pnl:.2f} USDC")
    print("=" * 60)


if __name__ == "__main__":
    main()
