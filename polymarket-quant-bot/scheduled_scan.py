#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时扫描脚本
每 15 分钟运行一次市场扫描
"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from main import PolymarketQuantBot

def main():
    """定时运行"""
    print("\n" + "="*60)
    print("⏰ 定时扫描启动")
    print("="*60)
    
    bot = PolymarketQuantBot(use_real_api=False)  # 测试模式
    bot.run_daily()
    
    print("\n✅ 定时扫描完成")
    print("下次扫描：15 分钟后\n")

if __name__ == "__main__":
    main()
