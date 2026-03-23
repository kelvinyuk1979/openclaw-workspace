#!/usr/bin/env python3
"""
检查 OKX API 权限和账户状态
"""

import json
import requests
import hmac
import base64
import hashlib
from datetime import datetime

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
    
    # 测试 1: 获取账户信息
    print("=" * 60)
    print("🔍 OKX API 权限检查")
    print("=" * 60)
    
    timestamp = datetime.utcnow().isoformat(timespec='milliseconds').split('.')[0] + 'Z'
    method = 'GET'
    request_path = '/api/v5/account/balance'
    body = ''
    
    sign_val = sign(timestamp, method, request_path, body, secret_key)
    
    headers = {
        'OK-ACCESS-KEY': api_key,
        'OK-ACCESS-SIGN': sign_val,
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': passphrase,
        'Content-Type': 'application/json'
    }
    
    print("\n1️⃣ 查询账户余额...")
    response = requests.get(base_url + request_path, headers=headers)
    result = response.json()
    print(f"   响应码：{result.get('code')}")
    print(f"   响应消息：{result.get('msg')}")
    
    if result.get('code') == '0' and result.get('data'):
        data = result['data'][0]
        total_eq = data.get('totalEq', '0')
        print(f"   总权益：{total_eq} USDT")
        
        for detail in data.get('details', []):
            if detail.get('ccy') == 'USDT':
                avail_bal = detail.get('availBal', '0')
                print(f"   USDT 可用：{avail_bal}")
    
    # 测试 2: 获取账户配置
    print("\n2️⃣ 查询账户配置...")
    request_path = '/api/v5/account/config'
    timestamp = datetime.utcnow().isoformat(timespec='milliseconds').split('.')[0] + 'Z'
    sign_val = sign(timestamp, method, request_path, '', secret_key)
    headers['OK-ACCESS-TIMESTAMP'] = timestamp
    headers['OK-ACCESS-SIGN'] = sign_val
    
    response = requests.get(base_url + request_path, headers=headers)
    result = response.json()
    print(f"   响应码：{result.get('code')}")
    if result.get('data'):
        print(f"   账户配置：{result['data']}")
    
    # 测试 3: 获取持仓
    print("\n3️⃣ 查询当前持仓...")
    request_path = '/api/v5/account/positions'
    timestamp = datetime.utcnow().isoformat(timespec='milliseconds').split('.')[0] + 'Z'
    sign_val = sign(timestamp, method, request_path, '', secret_key)
    headers['OK-ACCESS-TIMESTAMP'] = timestamp
    headers['OK-ACCESS-SIGN'] = sign_val
    
    response = requests.get(base_url + request_path, headers=headers)
    result = response.json()
    print(f"   响应码：{result.get('code')}")
    print(f"   持仓数量：{len(result.get('data', []))}")
    
    # 测试 4: 获取 ETH 价格
    print("\n4️⃣ 获取 ETH 价格...")
    request_path = '/api/v5/market/ticker'
    params = {'instId': 'ETH-USDT'}
    timestamp = datetime.utcnow().isoformat(timespec='milliseconds').split('.')[0] + 'Z'
    sign_val = sign(timestamp, method, request_path + '?instId=ETH-USDT', '', secret_key)
    headers['OK-ACCESS-TIMESTAMP'] = timestamp
    headers['OK-ACCESS-SIGN'] = sign_val
    
    response = requests.get(base_url + request_path, params=params, headers=headers)
    result = response.json()
    print(f"   响应码：{result.get('code')}")
    if result.get('data'):
        print(f"   ETH 价格：${result['data'][0].get('last')}")
    
    print("\n" + "=" * 60)
    print("✅ 检查完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
