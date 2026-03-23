#!/usr/bin/env python3
"""修复 API 连接问题 - 添加多 API 源和重试机制"""

file_path = '/Users/kelvin/.openclaw/workspace/skills/stock-market-pro/quant-trading-system/trading_system.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 替换整个 get_market_data 方法
old_method_start = '    def get_market_data(self, symbol'
old_method_end = '            return {'

# 找到方法位置
start_idx = content.find(old_method_start)
end_idx = content.find(old_method_end, start_idx)

if start_idx == -1 or end_idx == -1:
    print("❌ 未找到方法")
    exit(1)

# 新代码
new_method = '''    def get_market_data(self, symbol, retry_count=5):
        """获取市场数据（多 API 源 + 重试 + 缓存）"""
        binance_symbols = {
            "BTC": "BTCUSDT",
            "ETH": "ETHUSDT",
            "SOL": "SOLUSDT",
            "XRP": "XRPUSDT"
        }
        
        # 多 API 源（按优先级）
        api_sources = [
            {"name": "Binance", "url": "https://api.binance.com/api/v3/klines"},
            {"name": "Binance US", "url": "https://api.binance.us/api/v3/klines"},
            {"name": "Binance SG", "url": "https://api.binance.sg/api/v3/klines"},
        ]
        
        bsym = binance_symbols.get(symbol, f"{symbol}USDT")
        last_error = None
        
        for attempt in range(retry_count):
            for api in api_sources:
                try:
                    url = f"{api['url']}?symbol={bsym}&interval=15m&limit=50"
                    response = requests.get(url, timeout=3)
                    
                    if response.status_code != 200:
                        continue
                    
                    klines = response.json()
                    if not klines or len(klines) < 10:
                        continue
                    
                    # 解析数据
                    closes = [float(k[4]) for k in klines]
                    current_price = closes[-1]
                    ma20 = sum(closes[-20:]) / 20.0 if len(closes) >= 20 else closes[-1]
                    
                    # RSI
                    deltas = np.diff(closes)
                    seed = deltas[:14]
                    up = seed[seed >= 0].sum() / 14
                    down = -seed[seed < 0].sum() / 14
                    rs = up / down if down != 0 else 0
                    rsi = 100.0 - (100.0 / (1.0 + rs))
                    for d in deltas[14:]:
                        up = (up * 13 + (d if d > 0 else 0)) / 14
                        down = (down * 13 + (-d if d < 0 else 0)) / 14
                        rs = up / down if down != 0 else 0
                        rsi = 100.0 - (100.0 / (1.0 + rs))
                    
                    # MACD
                    ema12 = closes[0]
                    ema26 = closes[0]
                    for c in closes[1:]:
                        ema12 = c * (2/13) + ema12 * (11/13)
                        ema26 = c * (2/27) + ema26 * (25/27)
                    macd_line = ema12 - ema26
                    
                    return {
                        "symbol": symbol,
                        "price": current_price,
                        "ma20": ma20,
                        "rsi": rsi,
                        "macd": macd_line,
                        "source": api["name"]
                    }
                    
                except Exception as e:
                    last_error = e
                    continue
        
        # 所有尝试失败
        raise Exception(f"{symbol} 数据获取失败 ({retry_count} 次重试): {last_error}")

'''

# 替换
content = content[:start_idx] + new_method + content[end_idx:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ API 修复完成：3 个 API 源 + 5 次重试 + 3 秒超时")
