#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股量化交易系统 - 每日运行脚本
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main_a_stock import AStockQuantSystem

def main():
    """主函数"""
    print("\n" + "="*60)
    print("🚀 A 股量化交易系统 - 每日运行")
    print("="*60)
    
    # 初始化系统
    system = AStockQuantSystem()
    
    # 运行每日交易
    system.run_daily()
    
    print("\n✅ A 股量化交易系统运行完成！")
    print("="*60)

if __name__ == "__main__":
    main()
