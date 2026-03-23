import re

with open('trading_system.py', 'r') as f:
    content = f.read()

# 1. 将 K 线周期改为 15m，更匹配 5 分钟检查频率
content = content.replace("interval=1h", "interval=15m")

# 2. 移除 fallback 到随机数的逻辑，改为安全防御模式
old_except = """        except Exception as e:
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

new_except = """        except Exception as e:
            print(f"⚠️ 获取 {symbol} 数据失败：{e}。进入安全模式，本轮暂停交易。")
            return None"""

content = content.replace(old_except, new_except)

# 3. 修复 get_consensus_signal 对 None 数据的处理
old_consensus = """    def get_consensus_signal(self, symbol):
        \"\"\"获取多策略共识信号\"\"\"
        data = self.get_market_data(symbol)
        
        votes = {"""

new_consensus = """    def get_consensus_signal(self, symbol):
        \"\"\"获取多策略共识信号\"\"\"
        data = self.get_market_data(symbol)
        
        if not data:
            return {
                "symbol": symbol,
                "data": None,
                "votes": {},
                "signal": "HOLD",
                "vote_count": {"LONG": 0, "SHORT": 0, "HOLD": 4}
            }
            
        votes = {"""

content = content.replace(old_consensus, new_consensus)

# 4. 修复 check_stop_loss_take_profit 对 None 数据的处理
old_check = """            current_data = self.get_market_data(symbol)
            current_price = current_data["price"]"""

new_check = """            current_data = self.get_market_data(symbol)
            if not current_data:
                continue  # 如果获取不到价格，跳过本轮止损止盈检查
            current_price = current_data["price"]"""

content = content.replace(old_check, new_check)

with open('trading_system.py', 'w') as f:
    f.write(content)
print("Quant System Optimized!")
