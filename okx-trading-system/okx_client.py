#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OKX API 客户端
支持行情获取、模拟交易
"""

import json
import hmac
import base64
import hashlib
import requests
from datetime import datetime
from pathlib import Path

class OKXClient:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parent / 'config' / 'config.json'
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.api_key = self.config['api_key']
        self.secret_key = self.config['secret_key']
        self.passphrase = self.config.get('passphrase', '')
        self.mode = self.config.get('mode', 'simulation')
        
        self.base_url = "https://www.okx.com"
        if self.mode == 'simulation':
            self.base_url = "https://www.okx.com"  # OKX 模拟盘也用正式 API
        
        self.session = requests.Session()
    
    def _sign(self, timestamp, method, request_path, body=''):
        """生成签名"""
        message = timestamp + method + request_path + body
        mac = hmac.new(
            bytes(self.secret_key, encoding='utf8'),
            bytes(message, encoding='utf8'),
            digestmod=hashlib.sha256
        )
        return base64.b64encode(mac.digest()).decode()
    
    def _get_headers(self, method, request_path, body=''):
        """生成请求头"""
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        sign = self._sign(timestamp, method, request_path, body)
        
        headers = {
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': sign,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }
        return headers
    
    def get_ticker(self, symbol):
        """获取行情数据"""
        try:
            # OKX 模拟盘 endpoint
            url = f"{self.base_url}/api/v5/market/ticker"
            params = {'instId': symbol}
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('code') == '0' and data.get('data'):
                ticker = data['data'][0]
                return {
                    'symbol': symbol,
                    'last': float(ticker.get('last', 0)),
                    'bid': float(ticker.get('bidPx', 0)),
                    'ask': float(ticker.get('askPx', 0)),
                    'high_24h': float(ticker.get('high24h', 0)),
                    'low_24h': float(ticker.get('low24h', 0)),
                    'volume_24h': float(ticker.get('vol24h', 0)),
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            print(f"获取行情失败：{e}")
        
        return None
    
    def get_candles(self, symbol, bar='1m', limit=100):
        """获取 K 线数据"""
        try:
            url = f"{self.base_url}/api/v5/market/candles"
            params = {'instId': symbol, 'bar': bar, 'limit': limit}
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('code') == '0' and data.get('data'):
                candles = []
                for c in data['data']:
                    candles.append({
                        'time': c[0],
                        'open': float(c[1]),
                        'high': float(c[2]),
                        'low': float(c[3]),
                        'close': float(c[4]),
                        'volume': float(c[5])
                    })
                return candles
        except Exception as e:
            print(f"获取 K 线失败：{e}")
        
        return []
    
    def get_account_balance(self):
        """获取账户余额（模拟）"""
        # 模拟账户数据
        return {
            'total': self.config.get('initial_capital', 10000),
            'available': self.config.get('initial_capital', 10000),
            'frozen': 0,
            'currency': 'USDT'
        }
    
    def place_order(self, symbol, side, size, price=None, order_type='market'):
        """下单交易（模拟）"""
        order = {
            'order_id': f"SIM_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'size': size,
            'price': price,
            'status': 'filled',
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"📝 [模拟] {side} {symbol} {size} @ {price or 'market'}")
        return order
    
    def cancel_order(self, symbol, order_id):
        """取消订单（模拟）"""
        print(f"❌ [模拟] 取消订单 {order_id}")
        return {'success': True}
    
    def get_positions(self):
        """获取持仓（模拟）"""
        return []
    
    def test_connection(self):
        """测试连接"""
        try:
            ticker = self.get_ticker('BTC-USDT')
            if ticker:
                return True, f"连接成功，BTC 价格：${ticker['last']}"
            return False, "无法获取行情"
        except Exception as e:
            return False, str(e)


if __name__ == '__main__':
    client = OKXClient()
    success, msg = client.test_connection()
    print(f"连接测试：{msg}")
    
    if success:
        print("\n获取 BTC 行情:")
        ticker = client.get_ticker('BTC-USDT')
        print(json.dumps(ticker, indent=2, ensure_ascii=False))
