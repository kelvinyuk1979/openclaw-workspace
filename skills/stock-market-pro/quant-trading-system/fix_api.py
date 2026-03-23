#!/usr/bin/env python3
"""修复 API 连接问题 - 添加重试机制"""

import re

file_path = '/Users/kelvin/.openclaw/workspace/skills/stock-market-pro/quant-trading-system/trading_system.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 替换 get_market_data 方法
old_method = '''    def get_market_data(self, symbol):
        """获取市场数据（使用 Binance API 获取真实数据）"""
        binance_symbols = {
            "BTC": "BTCUSDT",
            "ETH": "ETHUSDT",
            "SOL": "SOLUSDT",
            "XRP": "XRPUSDT"
        }
        
        try:
            bsym = binance_symbols.get(symbol, f"{symbol}USDT")
            url = f"https://api.binance.com/api/v3/klines?symbol={bsym}&interval=15m&limit=50"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                raise Exception(f"Binance API 状态码：{response.status_code}")
                
            klines = response.json()
            if not klines or len(klines) < 30:
                raise Exception("K 线数据不足")
                
            # 解析收盘价
            closes = [float(k[4]) for k in klines]
            current_price = closes[-1]'''

new_method = '''    def get_market_data(self, symbol, retry_count=3):
        """获取市场数据（多 API 源 + 重试机制）"""
        binance_symbols = {
            "BTC": "BTCUSDT",
            "ETH": "ETHUSDT",
            "SOL": "SOLUSDT",
            "XRP": "XRPUSDT"
        }
        
        last_error = None
        
        for attempt in range(retry_count):
            # 尝试不同 API 源
            api_urls = [
                f"https://api.binance.com/api/v3/klines?symbol={binance_symbols.get(symbol, f'{symbol}USDT')}&interval=15m&limit=50",
                f"https://api.binance.us/api/v3/klines?symbol={binance_symbols.get(symbol, f'{symbol}USDT')}&interval=15m&limit=50",
            ]
            
            for url in api_urls:
                try:
                    response = requests.get(url, timeout=5)
                    
                    if response.status_code != 200:
                        continue
                        
                    klines = response.json()
                    if not klines or len(klines) < 10:
                        continue
                        
                    # 解析收盘价
                    closes = [float(k[4]) for k in klines]
                    current_price = closes[-1]
                    break
                    
                except Exception as e:
                    last_error = e
                    continue
            else:
                continue
            break
        else:
            raise Exception(f"获取数据失败 ({retry_count} 次重试): {last_error}")'''

if old_method in content:
    content = content.replace(old_method, new_method)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ 修复完成：添加了重试机制和多 API 源")
else:
    print("⚠️  未找到匹配的代码，可能已修改")
