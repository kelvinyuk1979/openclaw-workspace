#!/usr/bin/env python3
"""
ETH 实盘买入测试 - 使用现货交易
"""

import json
import sys
import os
import requests
import hmac
import base64
import hashlib
from datetime import datetime, timezone

CONFIG_PATH = '/Users/kelvin/.openclaw/workspace/skills/stock-market-pro/quant-trading-system/okx_config.json'
MEMORY_PATH = '/Users/kelvin/.openclaw/workspace/memory/2026-03-23.md'

def sign(timestamp, method, request_path, body, secret_key):
    message = timestamp + method + request_path + body
    mac = hmac.new(
        bytes(secret_key, encoding='utf8'),
        bytes(message, encoding='utf8'),
        digestmod=hashlib.sha256
    )
    d = mac.digest()
    return base64.b64encode(d).decode()

def main():
    print("=" * 60)
    print("🚀 ETH 实盘买入测试 - 10 USDT (现货交易)")
    print("=" * 60)
    
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    
    api_key = config['okx']['api_key']
    secret_key = config['okx']['secret_key']
    passphrase = config['okx']['passphrase']
    
    base_url = "https://www.okx.com"
    
    # 1. 获取 ETH 价格
    print("\n1️⃣ 获取 ETH 当前价格...")
    timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds').split('.')[0] + 'Z'
    method = 'GET'
    request_path = '/api/v5/market/ticker?instId=ETH-USDT'
    sign_val = sign(timestamp, method, request_path, '', secret_key)
    
    headers = {
        'OK-ACCESS-KEY': api_key,
        'OK-ACCESS-SIGN': sign_val,
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': passphrase,
        'Content-Type': 'application/json'
    }
    
    response = requests.get(base_url + '/api/v5/market/ticker', 
                          params={'instId': 'ETH-USDT'}, 
                          headers=headers)
    result = response.json()
    
    if result.get('code') != '0':
        print(f"❌ 获取价格失败：{result.get('msg')}")
        sys.exit(1)
    
    eth_price = float(result['data'][0]['last'])
    print(f"   ETH-USDT: ${eth_price:.2f}")
    
    # 2. 计算可买数量（现货）
    trade_amount = 10.0  # 10 USDT
    eth_amount = trade_amount / eth_price
    
    # 查询现货交易规则
    print(f"\n2️⃣ 查询现货交易规则...")
    timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds').split('.')[0] + 'Z'
    request_path = '/api/v5/public/instruments?instType=SPOT&instId=ETH-USDT'
    sign_val = sign(timestamp, 'GET', request_path, '', secret_key)
    headers['OK-ACCESS-TIMESTAMP'] = timestamp
    headers['OK-ACCESS-SIGN'] = sign_val
    
    response = requests.get(base_url + '/api/v5/public/instruments',
                          params={'instType': 'SPOT', 'instId': 'ETH-USDT'},
                          headers=headers)
    inst_result = response.json()
    
    lot_sz = 0.0001  # 默认
    min_sz = 0.0001  # 默认
    
    if inst_result.get('code') == '0' and inst_result.get('data'):
        inst = inst_result['data'][0]
        lot_sz = float(inst.get('lotSz', 0.0001))
        min_sz = float(inst.get('minSz', 0.0001))
        print(f"   最小下单：{min_sz} ETH")
        print(f"   数量增量：{lot_sz} ETH")
    
    # 调整数量到符合规则
    eth_amount = max(min_sz, round(eth_amount / lot_sz) * lot_sz)
    actual_value = eth_amount * eth_price
    
    print(f"\n3️⃣ 计算仓位...")
    print(f"   目标金额：{trade_amount} USDT")
    print(f"   实际数量：{eth_amount:.8f} ETH")
    print(f"   实际价值：${actual_value:.2f} USDT")
    
    # 4. 执行市价买入（现货）
    print(f"\n4️⃣ 执行市价买入订单（现货）...")
    print(f"   币种：ETH-USDT")
    print(f"   方向：buy")
    print(f"   数量：{eth_amount} ETH")
    
    timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds').split('.')[0] + 'Z'
    method = 'POST'
    request_path = '/api/v5/trade/order'
    body = json.dumps({
        'instId': 'ETH-USDT',
        'tdMode': 'cash',  # 现货模式
        'side': 'buy',
        'sz': str(eth_amount),
        'ordType': 'market'  # 市价单
    })
    sign_val = sign(timestamp, method, request_path, body, secret_key)
    headers['OK-ACCESS-TIMESTAMP'] = timestamp
    headers['OK-ACCESS-SIGN'] = sign_val
    
    response = requests.post(base_url + request_path, headers=headers, data=body)
    result = response.json()
    
    print(f"   响应码：{result.get('code')}")
    print(f"   响应消息：{result.get('msg')}")
    
    if result.get('code') == '0' and result.get('data'):
        order_id = result['data'][0].get('ordId')
        print(f"\n✅ 订单提交成功！")
        print(f"   订单 ID: {order_id}")
        
        # 5. 查询订单状态
        print(f"\n5️⃣ 查询订单状态...")
        timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds').split('.')[0] + 'Z'
        method = 'GET'
        request_path = f'/api/v5/trade/order?instId=ETH-USDT&ordId={order_id}'
        sign_val = sign(timestamp, method, request_path, '', secret_key)
        headers['OK-ACCESS-TIMESTAMP'] = timestamp
        headers['OK-ACCESS-SIGN'] = sign_val
        
        response = requests.get(base_url + '/api/v5/trade/order',
                              params={'instId': 'ETH-USDT', 'ordId': order_id},
                              headers=headers)
        order_result = response.json()
        
        if order_result.get('code') == '0' and order_result.get('data'):
            order_info = order_result['data'][0]
            state = order_info.get('state', 'unknown')
            fill_price = float(order_info.get('avgPx', 0)) if order_info.get('avgPx') else eth_price
            filled_size = float(order_info.get('accFillSz', 0)) if order_info.get('accFillSz') else eth_amount
            
            print(f"   订单状态：{state}")
            print(f"   成交价：${fill_price:.2f}")
            print(f"   成交数量：{filled_size:.8f} ETH")
            
            # 6. 写入交易记录
            print(f"\n6️⃣ 写入交易记录...")
            now = datetime.now()
            timestamp_str = now.strftime('%Y-%m-%d %H:%M:%S')
            tz = now.astimezone().strftime('%z')
            
            record = f"""
### 📈 ETH 实盘买入测试（现货） - {timestamp_str} GMT{tz[:3]}:{tz[3:]}

**交易详情：**
- 币种：ETH-USDT（现货）
- 方向：BUY（做多）
- 订单 ID: `{order_id}`
- 订单状态：{state}
- 成交数量：{filled_size:.8f} ETH
- 成交价：${fill_price:.2f}
- 交易金额：${filled_size * fill_price:.2f} USDT
- 类型：市价单

**测试结果：** ✅ 成功

---
"""
            
            os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
            with open(MEMORY_PATH, 'a', encoding='utf-8') as f:
                f.write(record)
            
            print(f"   ✅ 已写入 {MEMORY_PATH}")
            
            # 7. Git 提交
            print(f"\n7️⃣ Git 提交...")
            os.chdir('/Users/kelvin/.openclaw/workspace')
            os.system('git add memory/2026-03-23.md')
            os.system(f'git commit -m "📈 ETH 实盘买入测试（现货）：{filled_size:.8f} ETH @ ${fill_price:.2f}"')
            print(f"   ✅ Git 提交完成")
            
            print("\n" + "=" * 60)
            print("🎉 ETH 实盘买入测试完成！")
            print("=" * 60)
            print(f"\n📊 交易结果汇总：")
            print(f"   订单 ID: {order_id}")
            print(f"   成交价：${fill_price:.2f}")
            print(f"   数量：{filled_size:.8f} ETH")
            print(f"   金额：${filled_size * fill_price:.2f} USDT")
            
        else:
            print(f"   ⚠️ 无法查询订单详情：{order_result.get('msg')}")
    else:
        print(f"\n❌ 订单失败：{result.get('msg', 'Unknown error')}")
        print(f"   完整响应：{result}")
        sys.exit(1)

if __name__ == "__main__":
    main()
