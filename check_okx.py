#!/usr/bin/env python3
import requests
import json
import time
import hmac
import base64
from datetime import datetime

# 读取 OKX API 配置
with open('skills/stock-market-pro/quant-trading-system/okx_config.json', 'r') as f:
    config = json.load(f)

API_KEY = config['okx']['api_key']
SECRET_KEY = config['okx']['secret_key']
PASSPHRASE = config['okx']['passphrase']
BASE_URL = 'https://www.okx.com'

def generate_signature(timestamp, method, path, body=''):
    message = timestamp + method + path + body
    mac = hmac.new(
        bytes(SECRET_KEY, encoding='utf8'),
        bytes(message, encoding='utf8'),
        digestmod='sha256'
    )
    return base64.b64encode(mac.digest()).decode()

def okx_request(method, path, body=''):
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    signature = generate_signature(timestamp, method, path, body)
    
    headers = {
        'OK-ACCESS-KEY': API_KEY,
        'OK-ACCESS-SIGN': signature,
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': PASSPHRASE,
        'Content-Type': 'application/json'
    }
    
    url = BASE_URL + path
    if method == 'GET':
        response = requests.get(url, headers=headers)
    else:
        response = requests.post(url, headers=headers, data=body)
    
    return response.json()

# 1. 检查 API 连接
print('=== 1. OKX API 连接检查 ===')
try:
    account_info = okx_request('GET', '/api/v5/account/balance')
    if account_info.get('code') == '0':
        print('✅ API 连接正常')
    else:
        print(f'❌ API 错误：{account_info}')
except Exception as e:
    print(f'❌ 连接失败：{e}')

# 2. 查询账户余额
print('\n=== 2. 账户余额 ===')
try:
    balance_data = account_info.get('data', [{}])[0]
    details = balance_data.get('details', [])
    
    total_equity = 0
    usdt_balance = 0
    
    for detail in details:
        if detail.get('ccy') == 'USDT':
            usdt_balance = float(detail.get('eq', 0))
            total_equity += usdt_balance
        elif detail.get('ccy') not in ['', '0']:
            qty = float(detail.get('eq', 0))
            if qty > 0:
                print(f"  {detail['ccy']}: {qty}")
    
    print(f"总权益：{total_equity:.2f} USDT")
    print(f"可用余额：{usdt_balance:.2f} USDT")
except Exception as e:
    print(f'❌ 读取余额失败：{e}')

# 3. 检查持仓状态
print('\n=== 3. 当前持仓 ===')
try:
    positions = okx_request('GET', '/api/v5/account/positions')
    pos_data = positions.get('data', [])
    
    if not pos_data:
        print('无持仓')
    else:
        for pos in pos_data:
            if float(pos.get('pos', 0)) != 0:
                print(f"  {pos['instId']}: {pos['pos']} {pos['ccy']} | 未实现盈亏：{pos['upl']} USDT")
except Exception as e:
    print(f'❌ 读取持仓失败：{e}')

# 4. 获取 BTC/ETH 价格
print('\n=== 4. BTC/ETH 价格 ===')
try:
    btc_ticker = okx_request('GET', '/api/v5/market/ticker?instId=BTC-USDT')
    eth_ticker = okx_request('GET', '/api/v5/market/ticker?instId=ETH-USDT')
    
    btc_price = float(btc_ticker.get('data', [{}])[0].get('last', 0))
    eth_price = float(eth_ticker.get('data', [{}])[0].get('last', 0))
    
    print(f'BTC: ${btc_price:.2f}')
    print(f'ETH: ${eth_price:.2f}')
except Exception as e:
    print(f'❌ 获取价格失败：{e}')

print('\n=== 检查完成 ===')
