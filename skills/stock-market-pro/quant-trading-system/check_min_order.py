#!/usr/bin/env python3
"""
查询 ETH-USDT 现货交易最小订单金额
"""

import json
import requests
import hmac
import base64
import hashlib
from datetime import datetime, timezone

CONFIG_PATH = '/Users/kelvin/.openclaw/workspace/skills/stock-market-pro/quant-trading-system/okx_config.json'

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
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    
    api_key = config['okx']['api_key']
    secret_key = config['okx']['secret_key']
    passphrase = config['okx']['passphrase']
    
    base_url = "https://www.okx.com"
    
    print("=" * 60)
    print("📋 查询 ETH-USDT 现货交易规则")
    print("=" * 60)
    
    timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds').split('.')[0] + 'Z'
    method = 'GET'
    request_path = '/api/v5/public/instruments?instType=SPOT&instId=ETH-USDT'
    sign_val = sign(timestamp, method, request_path, '', secret_key)
    
    headers = {
        'OK-ACCESS-KEY': api_key,
        'OK-ACCESS-SIGN': sign_val,
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': passphrase,
        'Content-Type': 'application/json'
    }
    
    response = requests.get(base_url + '/api/v5/public/instruments',
                          params={'instType': 'SPOT', 'instId': 'ETH-USDT'},
                          headers=headers)
    result = response.json()
    
    if result.get('code') == '0' and result.get('data'):
        inst = result['data'][0]
        print(f"\n币种：{inst.get('instId')}")
        print(f"交易类型：{inst.get('instType')}")
        print(f"最小下单数量：{inst.get('minSz')} ETH")
        print(f"数量增量：{inst.get('lotSz')} ETH")
        print(f"报价精度：{inst.get('tickSz')} USDT")
        print(f"基础货币：{inst.get('baseCcy')}")
        print(f"报价货币：{inst.get('quoteCcy')}")
        
        # 计算最小订单金额
        min_sz = float(inst.get('minSz', 0))
        lot_sz = float(inst.get('lotSz', 0))
        
        # 获取当前价格
        ticker_path = '/api/v5/market/ticker?instId=ETH-USDT'
        timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds').split('.')[0] + 'Z'
        sign_val = sign(timestamp, 'GET', ticker_path, '', secret_key)
        headers['OK-ACCESS-TIMESTAMP'] = timestamp
        headers['OK-ACCESS-SIGN'] = sign_val
        
        response = requests.get(base_url + '/api/v5/market/ticker',
                              params={'instId': 'ETH-USDT'},
                              headers=headers)
        ticker = response.json()
        
        if ticker.get('code') == '0':
            price = float(ticker['data'][0]['last'])
            min_order_value = min_sz * price
            print(f"\n💡 最小订单金额计算：")
            print(f"   最小数量：{min_sz} ETH")
            print(f"   当前价格：${price:.2f}")
            print(f"   最小订单价值：${min_order_value:.2f} USDT")
            
            print(f"\n📊 建议测试金额：")
            print(f"   最小：${min_order_value:.2f} USDT")
            print(f"   建议：${max(15, min_order_value * 1.5):.2f} USDT 以上")
    else:
        print(f"❌ 查询失败：{result.get('msg')}")
        
        # 尝试无需签名
        print("\n尝试无需签名查询...")
        response = requests.get(base_url + '/api/v5/public/instruments',
                              params={'instType': 'SPOT', 'instId': 'ETH-USDT'})
        result = response.json()
        
        if result.get('code') == '0' and result.get('data'):
            inst = result['data'][0]
            print(f"✅ 获取成功：")
            print(f"   最小下单：{inst.get('minSz')} ETH")
            print(f"   数量增量：{inst.get('lotSz')} ETH")

if __name__ == "__main__":
    main()
