#!/usr/bin/env python3
"""从 OKX API 获取真实持仓并更新本地数据"""

import requests, hmac, hashlib, base64, json, time
from pathlib import Path

API_KEY = 'a2bec7ba-cfd9-43d0-9118-16647f61dcf8'
SECRET_KEY = '108923178673A9DBB7207E2538C75E2F'
PASSPHRASE = 'Kelvinyuk@1979'

def okx_request(endpoint, max_retries=3):
    """OKX API 请求（带重试）"""
    for i in range(max_retries):
        try:
            timestamp = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
            method = 'GET'
            prehash = timestamp + method + endpoint
            signature = base64.b64encode(hmac.new(SECRET_KEY.encode(), prehash.encode(), hashlib.sha256).digest()).decode()
            
            headers = {
                'OK-ACCESS-KEY': API_KEY,
                'OK-ACCESS-SIGN': signature,
                'OK-ACCESS-TIMESTAMP': timestamp,
                'OK-ACCESS-PASSPHRASE': PASSPHRASE,
                'Content-Type': 'application/json'
            }
            
            resp = requests.get('https://www.okx.com' + endpoint, headers=headers, timeout=10)
            data = resp.json()
            
            if data.get('code') == '0':
                return data.get('data', [])
            else:
                print(f"API 错误：{data}")
                return None
        except Exception as e:
            print(f"重试 {i+1}/{max_retries}: {e}")
            if i < max_retries - 1:
                time.sleep(2)
    return None

# 获取账户余额
print("1️⃣ 获取账户余额...")
balance_data = okx_request('/api/v5/account/balance')
if balance_data:
    for item in balance_data:
        details = item.get('details', [])
        usdt = next((d for d in details if d.get('ccy') == 'USDT'), {})
        total_eq = usdt.get('eq', '0')
        avail_eq = usdt.get('availEq', '0')
        print(f"   总权益：{total_eq} USDT")
        print(f"   可用：{avail_eq} USDT")

# 获取持仓
print("\n2️⃣ 获取持仓...")
positions = okx_request('/api/v5/account/positions?instType=MARGIN')
if positions:
    print(f"   持仓数：{len(positions)}")
    for pos in positions:
        inst_id = pos.get('instId', '')
        amount = pos.get('pos', '0')
        avg_px = pos.get('avgPx', '0')
        print(f"   - {inst_id}: {amount} @ {avg_px}")
    
    # 更新本地数据
    if positions:
        print("\n3️⃣ 更新本地数据...")
        
        # 获取当前价格
        btc_price = okx_request('/api/v5/market/ticker?instId=BTC-USDT')
        eth_price = okx_request('/api/v5/market/ticker?instId=ETH-USDT')
        
        btc_current = float(btc_price[0]['last']) if btc_price else 70540
        eth_current = float(eth_price[0]['last']) if eth_price else 2146
        
        # 构建持仓数据
        btc_pos = next((p for p in positions if 'BTC' in p.get('instId', '')), None)
        eth_pos = next((p for p in positions if 'ETH' in p.get('instId', '')), None)
        
        account_data = {
            "initial_capital": 143.85,
            "balance": float(avail_eq) if avail_eq else 7.11,
            "total_pnl": 0,
            "created_at": "2026-03-23T12:18:00+08:00",
            "last_updated": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            "positions": []
        }
        
        if btc_pos:
            btc_amount = float(btc_pos.get('pos', 0))
            btc_avg = float(btc_pos.get('avgPx', 0))
            btc_cost = btc_amount * btc_avg
            btc_pnl_pct = ((btc_current - btc_avg) / btc_avg) * 100
            account_data["positions"].append({
                "symbol": "BTC",
                "amount": btc_amount,
                "avg_price": btc_avg,
                "side": "LONG",
                "cost": btc_cost,
                "current_price": btc_current,
                "pnl_pct": round(btc_pnl_pct, 2)
            })
        
        if eth_pos:
            eth_amount = float(eth_pos.get('pos', 0))
            eth_avg = float(eth_pos.get('avgPx', 0))
            eth_cost = eth_amount * eth_avg
            eth_pnl_pct = ((eth_current - eth_avg) / eth_avg) * 100
            account_data["positions"].append({
                "symbol": "ETH",
                "amount": eth_amount,
                "avg_price": eth_avg,
                "side": "LONG",
                "cost": eth_cost,
                "current_price": eth_current,
                "pnl_pct": round(eth_pnl_pct, 2)
            })
        
        # 计算总盈亏
        total_pnl = sum(p['cost'] * p['pnl_pct'] / 100 for p in account_data["positions"])
        account_data["total_pnl"] = round(total_pnl, 2)
        
        # 写入文件
        data_dir = Path(__file__).parent / 'data'
        data_dir.mkdir(exist_ok=True)
        
        with open(data_dir / 'account.json', 'w', encoding='utf-8') as f:
            json.dump(account_data, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ 已更新 account.json")
        print(f"   BTC: {btc_amount if btc_pos else 0} @ {btc_avg if btc_pos else 0}")
        print(f"   ETH: {eth_amount if eth_pos else 0} @ {eth_avg if eth_pos else 0}")
else:
    print("   ❌ 获取持仓失败")
