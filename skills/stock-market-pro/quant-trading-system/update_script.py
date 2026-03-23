import re

with open('trading_system.py', 'r') as f:
    content = f.read()

new_get_market_data = """    def get_market_data(self, symbol):
        \"\"\"获取市场数据（使用 Binance API 获取真实数据）\"\"\"
        binance_symbols = {
            "BTC": "BTCUSDT",
            "ETH": "ETHUSDT",
            "SOL": "SOLUSDT",
            "XRP": "XRPUSDT"
        }
        
        try:
            bsym = binance_symbols.get(symbol, f"{symbol}USDT")
            url = f"https://api.binance.com/api/v3/klines?symbol={bsym}&interval=1h&limit=50"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                raise Exception(f"Binance API 状态码：{response.status_code}")
                
            klines = response.json()
            if not klines or len(klines) < 30:
                raise Exception("K线数据不足")
                
            # 解析收盘价
            closes = [float(k[4]) for k in klines]
            current_price = closes[-1]
            
            # 计算 MA20
            ma20 = sum(closes[-20:]) / 20.0
            
            # 计算 RSI (14)
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
                
            # 计算 MACD (12, 26, 9)
            ema12 = closes[0]
            ema26 = closes[0]
            for c in closes[1:]:
                ema12 = c * (2/13) + ema12 * (11/13)
                ema26 = c * (2/27) + ema26 * (25/27)
            macd_line = ema12 - ema26
            
            return {
                "price": current_price,
                "rsi": rsi,
                "macd": macd_line,
                "ma20": ma20,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"⚠️ 获取 {symbol} 数据失败：{e}，使用回退数据")
            import random
            price = {"BTC": 68000, "ETH": 3500, "SOL": 145, "XRP": 0.52}.get(symbol, 100)
            return {
                "price": price,
                "rsi": 30 + random.random() * 40,
                "macd": (random.random() - 0.5) * 100,
                "ma20": price,
                "timestamp": datetime.now().isoformat()
            }"""

# 替换
pattern = re.compile(r'    def get_market_data\(self, symbol\):.*?    def strategy_momentum\(self, data\):', re.DOTALL)
new_content = pattern.sub(new_get_market_data + "\n\n    def strategy_momentum(self, data):", content)

with open('trading_system.py', 'w') as f:
    f.write(new_content)
print("Updated trading_system.py")
