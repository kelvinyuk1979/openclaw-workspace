#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polymarket 天气交易机器人 - 每日自动运行脚本
1. 运行机器人获取最新数据
2. 保存今日信号
3. 生成并发送邮件报告
"""

import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent

def run_bot():
    """运行机器人获取数据"""
    print("🤖 运行天气交易机器人...")
    
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / 'bot_v1.py'), '--quiet', '--live'],
        capture_output=True,
        text=True,
        cwd=SCRIPT_DIR
    )
    
    if result.returncode != 0:
        print(f"❌ 机器人运行失败：{result.stderr}")
        return False
    
    print("✅ 机器人运行完成")
    return True


def extract_signals(output: str) -> list:
    """从输出中提取信号"""
    signals = []
    # 这里需要解析 bot_v1.py 的输出
    # 简化版本：直接从 simulation.json 读取
    return signals


def save_signals(signals: list):
    """保存今日信号"""
    signals_file = SCRIPT_DIR / 'today_signals.json'
    with open(signals_file, 'w', encoding='utf-8') as f:
        json.dump(signals, f, ensure_ascii=False, indent=2)
    print(f"📝 已保存 {len(signals)} 个信号")


def send_report():
    """发送邮件报告"""
    print("📧 发送邮件报告...")
    
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / 'send_daily_email.py')],
        capture_output=True,
        text=True,
        cwd=SCRIPT_DIR
    )
    
    if result.returncode != 0:
        print(f"❌ 邮件发送失败：{result.stderr}")
        return False
    
    print("✅ 邮件已发送")
    return True


def main():
    """主函数"""
    print("="*50)
    print(f"🌤️ Polymarket 天气机器人 - 每日运行")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    # 1. 运行机器人
    if not run_bot():
        return 1
    
    # 2. 保存信号（从 simulation.json 提取）
    sim_file = SCRIPT_DIR / 'simulation.json'
    if sim_file.exists():
        with open(sim_file, 'r', encoding='utf-8') as f:
            sim_data = json.load(f)
        
        # 提取信号（简化：从持仓和交易记录推断）
        signals = sim_data.get('trades', [])[-24:]  # 最近 24 个信号
        save_signals(signals)
    
    # 3. 发送邮件
    send_report()
    
    print("="*50)
    print("✅ 每日运行完成")
    print("="*50)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
