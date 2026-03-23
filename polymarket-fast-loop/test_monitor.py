#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Monitor 模块
"""

import logging
import sys
sys.path.insert(0, '.')

from monitor import PolymarketMonitor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 测试
api_key = "test_key"
monitor = PolymarketMonitor(api_key)

print("=" * 70)
print("🔍 测试市场获取")
print("=" * 70)
print()

markets = monitor.get_markets(limit=10)

print(f"\n📊 获取到 {len(markets)} 个市场")
print()

if markets:
    print("前 5 个市场:")
    print("-" * 70)
    for i, m in enumerate(markets[:5], 1):
        print(f"{i}. {m['title'][:60]}...")
        print(f"   ID: {m['id']}")
        print(f"   YES 价格：{m['yesBid']:.4f} | NO 价格：{m['noBid']:.4f}")
        print(f"   交易量：${m['volume']:,.2f} | 流动性：${m['liquidity']:,.2f}")
        print(f"   状态：{'活跃' if m['active'] else '已结束'}")
        print()
else:
    print("⚠️  未获取到市场数据")

print("=" * 70)
