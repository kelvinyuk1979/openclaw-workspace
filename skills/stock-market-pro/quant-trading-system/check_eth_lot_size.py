#!/usr/bin/env python3
"""
查询 ETH-USDT-SWAP 交易规则
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
    print("📋 查询 ETH-USDT-SWAP 交易规则")
    print("=" * 60)
    
    # 获取合约信息
    timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds').split('.')[0] + 'Z'
    method = 'GET'
    request_path = '/api/v5/public/instruments?instType=SWAP&instId=ETH-USDT-SWAP'
    sign_val = sign(timestamp, method, request_path, '', secret_key)
    
    headers = {
        'OK-ACCESS-KEY': api_key,
        'OK-ACCESS-SIGN': sign_val,
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': passphrase,
        'Content-Type': 'application/json'
    }
    
    response = requests.get(base_url + '/api/v5/public/instruments',
                          params={'instType': 'SWAP', 'instId': 'ETH-USDT-SWAP'},
                          headers=headers)
    result = response.json()
    
    if result.get('code') == '0' and result.get('data'):
        inst = result['data'][0]
        print(f"\n币种：{inst.get('instId')}")
        print(f"合约价值：{inst.get('ctVal')} ETH")
        print(f"最小下单数量：{inst.get('minSz')} 张")
        print(f"下单数量增量：{inst.get('lotSz')} 张")
        print(f"报价单位：{inst.get('tickSz')} USDT")
        
        # 计算实际可交易数量
        lot_sz = float(inst.get('lotSz', 1))
        min_sz = float(inst.get('minSz', 1))
        ct_val = float(inst.get('ctVal', 1)) if inst.get('ctVal') else 1
        
        print(f"\n💡 交易规则说明：")
        print(f"   - 1 张合约 = {ct_val} ETH")
        print(f"   - 最小下单：{min_sz} 张")
        print(f"   - 数量增量：{lot_sz} 张的倍数")
        
        # 计算 10 USDT 对应的张数
        print(f"\n📊 计算 10 USDT 仓位：")
        print(f"   如果 1 张=0.01 ETH，ETH=$2050，则 1 张价值≈$20.5")
        print(f"   10 USDT 约可买：{10/20.5:.2f} 张")
        
    else:
        print(f"❌ 查询失败：{result.get('msg')}")
        
        # 尝试不签名获取公开信息
        print("\n尝试无需签名查询...")
        response = requests.get(base_url + '/api/v5/public/instruments',
                              params={'instType': 'SWAP', 'instId': 'ETH-USDT-SWAP'})
        result = response.json()
        
        if result.get('code') == '0' and result.get('data'):
            inst = result['data'][0]
            print(f"✅ 获取成功：")
            print(f"   币种：{inst.get('instId')}")
            print(f"   合约价值：{inst.get('ctVal')} ETH")
            print(f"   最小下单数量：{inst.get('minSz')} 张")
            print(f"   下单数量增量：{inst.get('lotSz')} 张")

if __name__ == "__main__":
    main()
