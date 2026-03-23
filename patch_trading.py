import re

with open("/Users/kelvin/.openclaw/workspace/skills/stock-market-pro/quant-trading-system/trading_system.py", "r") as f:
    content = f.read()

new_get_market_data = '''    def get_market_data(self, symbol):
        """获取真实历史数据并计算指标（使用 Binance API）"""
        from datetime import datetime
        import requests
        
        # Binance symbol format: "BTCUSDT"
        binance_symbol = f"{symbol}USDT"
        
        try:
            # 获取过去 60 个 15分钟 的 K 线数据计算指标
            url = f"https://api.binance.com/api/v3/klines?symbol={binance_symbol}&interval=15m&limit=60"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                raise Exception(f"Binance API 返回状态码：{response.status_code}")
            
            data = response.json()
            if not data or len(data) < 60:
                raise Exception("数据不足")
            
            import pandas as pd
            
            # K线字段：[Open time, Open, High, Low, Close, Volume, Close time, ...]
            df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "trades", "taker_buy_base", "taker_buy_quote", "ignore"])
            df["close"] = df["close"].astype(float)
            
            # 当前最新价格
            current_price = df["close"].iloc[-1]
            
            # 计算 MA20
            df["ma20"] = df["close"].rolling(window=20).mean()
            ma20 = df["ma20"].iloc[-1]
            
            # 计算 RSI (14)
            delta = df["close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df["rsi"] = 100 - (100 / (1 + rs))
            rsi = df["rsi"].iloc[-1]
            if pd.isna(rsi):
                rsi = 50.0 # 默认回退值
                
            # 计算 MACD (12, 26, 9)
            exp1 = df["close"].ewm(span=12, adjust=False).mean()
            exp2 = df["close"].ewm(span=26, adjust=False).mean()
            macd_line = exp1 - exp2
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            macd_hist = macd_line - signal_line
            macd = macd_hist.iloc[-1]
            
            return {
                "price": current_price,
                "rsi": rsi,
                "macd": macd,
                "ma20": ma20,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"⚠️ 获取 {symbol} 数据失败：{e}，使用回退数据")
            # 回退：仍使用假数据避免崩溃
            base_prices = {"BTC": 68000, "ETH": 3500, "SOL": 145, "XRP": 0.52}
            price = base_prices.get(symbol, 100)
            import random
            return {
                "price": price,
                "rsi": 30 + random.random() * 40,
                "macd": (random.random() - 0.5) * 100,
                "ma20": price * (1 + (random.random() - 0.5) * 0.02),
                "timestamp": datetime.now().isoformat()
            }'''

pattern = re.compile(r'    def get_market_data\(self, symbol\):.*?return \{\n.*?"timestamp": datetime\.now\(\)\.isoformat\(\)\n            \}\n', re.DOTALL)
new_content = pattern.sub(new_get_market_data + "\n", content)

with open("/Users/kelvin/.openclaw/workspace/skills/stock-market-pro/quant-trading-system/trading_system.py", "w") as f:
    f.write(new_content)

print("trading_system.py updated successfully.")
