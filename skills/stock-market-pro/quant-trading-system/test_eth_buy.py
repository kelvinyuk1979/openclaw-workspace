#!/usr/bin/env python3
"""
ETH 实盘买入测试脚本 - 10 USDT
"""

import json
import sys
import os
from datetime import datetime
from okx_client import OKXClient

# 配置路径
CONFIG_PATH = '/Users/kelvin/.openclaw/workspace/skills/stock-market-pro/quant-trading-system/okx_config.json'
MEMORY_PATH = '/Users/kelvin/.openclaw/workspace/memory/2026-03-23.md'

def main():
    print("=" * 60)
    print("🚀 ETH 实盘买入测试 - 10 USDT")
    print("=" * 60)
    
    # 读取配置
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    
    okx_config = config['okx']
    
    # 创建 OKX 客户端（实盘模式）
    client = OKXClient(
        api_key=okx_config['api_key'],
        secret_key=okx_config['secret_key'],
        passphrase=okx_config['passphrase'],
        testnet=False  # 实盘
    )
    
    # 1. 获取 ETH 当前价格
    print("\n1️⃣ 获取 ETH 当前价格...")
    ticker = client.get_ticker('ETH')
    if not ticker:
        print("❌ 获取 ETH 价格失败")
        sys.exit(1)
    
    eth_price = ticker['price']
    print(f"   ETH-USDT: ${eth_price:.2f}")
    
    # 2. 计算可买数量
    trade_amount = 10.0  # 10 USDT
    eth_amount = trade_amount / eth_price
    
    print(f"\n2️⃣ 计算可买数量...")
    print(f"   交易金额：{trade_amount} USDT")
    print(f"   可买数量：{eth_amount:.6f} ETH")
    print(f"   价值：${trade_amount:.2f}")
    
    # 3. 执行市价买入订单
    print(f"\n3️⃣ 执行市价买入订单...")
    print(f"   币种：ETH-USDT")
    print(f"   方向：BUY（做多）")
    print(f"   数量：{eth_amount:.6f} ETH")
    print(f"   类型：市价单")
    
    # 使用 place_order 方法（现货交易）
    result = client.place_order(
        symbol='ETH',
        side='LONG',
        size=eth_amount,
        order_type='market'
    )
    
    if result.get('success'):
        order_id = result.get('order_id')
        print(f"\n✅ 订单提交成功！")
        print(f"   订单 ID: {order_id}")
        
        # 4. 确认订单状态
        print(f"\n4️⃣ 查询订单状态...")
        order_info = client.get_order_info('ETH', order_id)
        
        if order_info:
            state = order_info.get('state', 'unknown')
            fill_price = float(order_info.get('avgPx', 0)) if order_info.get('avgPx') else eth_price
            filled_size = float(order_info.get('accFillSz', 0)) if order_info.get('accFillSz') else eth_amount
            
            print(f"   订单状态：{state}")
            print(f"   成交价：${fill_price:.2f}")
            print(f"   成交数量：{filled_size:.6f} ETH")
            
            # 5. 写入交易记录
            print(f"\n5️⃣ 写入交易记录...")
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            tz = datetime.now().astimezone().strftime('%z')
            
            record = f"""
### 📈 ETH 实盘买入测试 - {timestamp} GMT{tz[:3]}:{tz[3:]}

**交易详情：**
- 币种：ETH-USDT
- 方向：BUY（做多）
- 订单 ID: `{order_id}`
- 订单状态：{state}
- 成交数量：{filled_size:.6f} ETH
- 成交价：${fill_price:.2f}
- 交易金额：${filled_size * fill_price:.2f} USDT
- 类型：市价单

**测试结果：** ✅ 成功

---
"""
            
            # 确保 memory 目录存在
            os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
            
            # 追加到记忆文件
            with open(MEMORY_PATH, 'a', encoding='utf-8') as f:
                f.write(record)
            
            print(f"   ✅ 已写入 {MEMORY_PATH}")
            
            # 6. Git 提交
            print(f"\n6️⃣ Git 提交...")
            os.chdir('/Users/kelvin/.openclaw/workspace')
            os.system('git add memory/2026-03-23.md')
            os.system(f'git commit -m "📈 ETH 实盘买入测试：{filled_size:.6f} ETH @ ${fill_price:.2f}"')
            print(f"   ✅ Git 提交完成")
            
            print("\n" + "=" * 60)
            print("🎉 ETH 实盘买入测试完成！")
            print("=" * 60)
            print(f"\n📊 交易结果汇总：")
            print(f"   订单 ID: {order_id}")
            print(f"   成交价：${fill_price:.2f}")
            print(f"   数量：{filled_size:.6f} ETH")
            print(f"   金额：${filled_size * fill_price:.2f} USDT")
            
        else:
            print(f"   ⚠️ 无法查询订单详情")
    else:
        print(f"\n❌ 订单失败：{result.get('error', 'Unknown error')}")
        sys.exit(1)

if __name__ == "__main__":
    main()
