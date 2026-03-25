#!/usr/bin/env python3
"""
OKX API 连接器 - 支持测试网和实盘
"""

import json
import hmac
import base64
import hashlib
import time
import requests
from datetime import datetime

class OKXClient:
    def __init__(self, api_key, secret_key, passphrase, testnet=True):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.testnet = testnet
        
        # API 端点
        if testnet:
            self.base_url = "https://www.okx.com"
            print("🔧 OKX 测试网模式")
        else:
            self.base_url = "https://www.okx.com"
            print("⚠️ OKX 实盘模式")
    
    def _sign(self, timestamp, method, request_path, body=""):
        """生成签名"""
        message = timestamp + method + request_path + body
        mac = hmac.new(
            bytes(self.secret_key, encoding='utf8'),
            bytes(message, encoding='utf8'),
            digestmod=hashlib.sha256
        )
        d = mac.digest()
        return base64.b64encode(d).decode()
    
    def _get_headers(self, method, request_path, body=""):
        """获取请求头"""
        timestamp = datetime.utcnow().isoformat(timespec='milliseconds').split('.')[0] + 'Z'
        sign = self._sign(timestamp, method, request_path, body)
        
        headers = {
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': sign,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }
        return headers
    
    def request(self, method, path, params=None):
        """通用请求方法"""
        url = self.base_url + path
        body = json.dumps(params) if params else ""
        
        headers = self._get_headers(method, path, body)
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=params, timeout=10)
            else:
                raise ValueError(f"不支持的方法：{method}")
            
            result = response.json()
            
            if result.get('code') != '0':
                raise Exception(f"OKX API 错误：{result.get('msg', 'Unknown error')}")
            
            return result.get('data', [])
            
        except Exception as e:
            raise Exception(f"OKX 请求失败：{e}")
    
    def get_balance(self, detailed=False):
        """获取账户余额
        
        Args:
            detailed: 如果为 True，返回完整的余额详情（用于调试数据偏差）
        """
        try:
            data = self.request('GET', '/api/v5/account/balance')
            if data:
                result = {
                    'USDT': 0,
                    'total_eq': 0,
                    'raw_details': {}  # 用于调试
                }
                
                # 记录总权益原始值
                total_eq_raw = data[0].get('totalEq', '0')
                result['totalEq_raw'] = total_eq_raw
                result['total_eq'] = float(total_eq_raw) if total_eq_raw and total_eq_raw.strip() else 0.0
                
                # 记录账户等级
                result['acctLv'] = data[0].get('acctLv', 'unknown')
                
                for detail in data[0].get('details', []):
                    ccy = detail.get('ccy', 'UNKNOWN')
                    # 记录每个币种的完整详情
                    result['raw_details'][ccy] = {
                        'availBal': detail.get('availBal', ''),
                        'availEq': detail.get('availEq', ''),
                        'cashBal': detail.get('cashBal', ''),
                        'eq': detail.get('eq', ''),
                        'frozenBal': detail.get('frozenBal', ''),
                        'ordFrozen': detail.get('ordFrozen', ''),
                        'upl': detail.get('upl', ''),
                        'stgyEq': detail.get('stgyEq', '')
                    }
                    
                    if ccy == 'USDT':
                        avail_bal = detail.get('availBal', '')
                        avail_eq = detail.get('availEq', '')
                        
                        if avail_bal and avail_bal.strip():
                            result['USDT'] = float(avail_bal)
                            result['used_field'] = 'availBal'
                        elif avail_eq and avail_eq.strip():
                            result['USDT'] = float(avail_eq)
                            result['used_field'] = 'availEq'
                        else:
                            result['USDT'] = 0.0
                            result['used_field'] = 'none'
                
                if detailed:
                    return result
                else:
                    return {'USDT': result['USDT'], 'total_eq': result['total_eq']}
            return {'USDT': 0, 'total_eq': 0}
        except Exception as e:
            print(f"⚠️ 获取余额失败：{e}")
            return {'USDT': 0, 'total_eq': 0}
    
    def get_ticker(self, symbol):
        """获取行情"""
        # OKX 格式：BTC-USDT
        inst_id = f"{symbol}-USDT"
        try:
            data = self.request('GET', '/api/v5/market/ticker', {'instId': inst_id})
            if data:
                # 安全转换 float
                def safe_float(val, default=0.0):
                    if val is None or val == '':
                        return default
                    try:
                        return float(val)
                    except (ValueError, TypeError):
                        return default
                
                return {
                    'price': safe_float(data[0].get('last', 0)),
                    'bid': safe_float(data[0].get('bidPx', 0)),
                    'ask': safe_float(data[0].get('askPx', 0)),
                    'volume_24h': safe_float(data[0].get('volCcy24h', 0))
                }
            return None
        except Exception as e:
            print(f"⚠️ 获取 {symbol} 行情失败：{e}")
            return None
    
    def get_klines(self, symbol, interval='15m', limit=50):
        """获取 K 线数据"""
        inst_id = f"{symbol}-USDT"
        try:
            data = self.request('GET', '/api/v5/market/candles', {
                'instId': inst_id,
                'bar': interval,
                'limit': limit
            })
            
            if data:
                # 安全转换 float
                def safe_float(val, default=0.0):
                    if val is None or val == '':
                        return default
                    try:
                        return float(val)
                    except (ValueError, TypeError):
                        return default
                
                # 解析 K 线：[time, open, high, low, close, vol, ...]
                klines = []
                for k in data:
                    klines.append({
                        'time': k[0],
                        'open': safe_float(k[1]),
                        'high': safe_float(k[2]),
                        'low': safe_float(k[3]),
                        'close': safe_float(k[4]),
                        'volume': safe_float(k[5])
                    })
                return klines
            return []
        except Exception as e:
            print(f"⚠️ 获取 {symbol} K 线失败：{e}")
            return []
    
    def open_position(self, symbol, side, size, leverage=10):
        """开仓（合约交易）
        
        Args:
            symbol: 币种（如 'BTC', 'ETH'）
            side: 方向（'buy' 做多，'sell' 做空）
            size: 数量（张数）
            leverage: 杠杆（默认 10x）
        
        Returns:
            dict: 订单结果 {'orderId': '...', 'status': 'filled'}
        """
        inst_id = f"{symbol}-USDT-SWAP"  # 永续合约
        
        # 设置杠杆
        try:
            self.request('POST', '/api/v5/account/set-leverage', {
                'instId': inst_id,
                'lever': str(leverage),
                'mgnMode': 'cross'  # 全仓模式
            })
            print(f"✅ 设置 {symbol} 杠杆：{leverage}x")
        except Exception as e:
            print(f"⚠️ 设置杠杆失败：{e}")
        
        # 下单
        try:
            # posSide: long（做多）或 short（做空）
            pos_side = 'long' if side == 'buy' else 'short'
            
            data = self.request('POST', '/api/v5/trade/order', {
                'instId': inst_id,
                'tdMode': 'cross',  # 全仓
                'side': side,
                'posSide': pos_side,
                'sz': str(size),
                'ordType': 'market'  # 市价单
            })
            
            if data and data[0].get('sCode') == '0':
                order_id = data[0].get('ordId')
                print(f"✅ 开仓成功：{side.upper()} {symbol} {size} 张，订单 ID: {order_id}")
                return {'orderId': order_id, 'status': 'submitted'}
            else:
                print(f"❌ 开仓失败：{data}")
                return {'error': data}
                
        except Exception as e:
            print(f"❌ 开仓异常：{e}")
            return {'error': str(e)}
    
    def close_position(self, symbol, side, size):
        """平仓
        
        Args:
            symbol: 币种
            side: 方向（与开仓相反）
            size: 数量
        """
        return self.open_position(symbol, side, size)
    
    def get_order_info(self, symbol, order_id):
        """获取订单信息"""
        inst_id = f"{symbol}-USDT-SWAP"
        try:
            data = self.request('GET', '/api/v5/trade/order', {
                'instId': inst_id,
                'ordId': order_id
            })
            return data[0] if data else None
        except Exception as e:
            print(f"⚠️ 获取订单信息失败：{e}")
            return None
    
    def place_order(self, symbol, side, size, price=None, order_type='market'):
        """下单"""
        inst_id = f"{symbol}-USDT"
        td_mode = 'cash'  # 现货模式
        
        params = {
            'instId': inst_id,
            'tdMode': td_mode,
            'side': 'buy' if side == 'LONG' else 'sell',
            'ordType': order_type,
            'sz': str(size)
        }
        
        if price and order_type == 'limit':
            params['px'] = str(price)
        
        try:
            data = self.request('POST', '/api/v5/trade/order', params)
            if data:
                return {
                    'success': True,
                    'order_id': data[0].get('ordId'),
                    'symbol': symbol,
                    'side': side,
                    'size': size,
                    'price': price
                }
            return {'success': False, 'error': 'No data'}
        except Exception as e:
            print(f"⚠️ 下单失败：{e}")
            return {'success': False, 'error': str(e)}
    
    def cancel_order(self, symbol, order_id):
        """撤单"""
        inst_id = f"{symbol}-USDT"
        try:
            data = self.request('POST', '/api/v5/trade/cancel-order', {
                'instId': inst_id,
                'ordId': order_id
            })
            return {'success': True, 'order_id': order_id}
        except Exception as e:
            print(f"⚠️ 撤单失败：{e}")
            return {'success': False, 'error': str(e)}
    
    def get_spot_positions(self):
        """获取现货持仓（从余额查询）"""
        try:
            data = self.request('GET', '/api/v5/account/balance')
            positions = {}
            for item in data:
                details = item.get('details', [])
                for d in details:
                    ccy = d.get('ccy', '')
                    eq = d.get('eq', '0')  # 权益（持仓数量）
                    if ccy in ['BTC', 'ETH'] and float(eq or 0) > 0:
                        # 获取当前价格
                        ticker = self.request('GET', f'/api/v5/market/ticker?instId={ccy}-USDT')
                        price = float(ticker[0]['last']) if ticker else 0
                        positions[ccy] = {
                            'side': 'LONG',
                            'size': float(eq),
                            'entry_price': 0,  # 现货余额不显示成本价
                            'current_price': price,
                            'pnl': 0,
                            'pnl_pct': 0
                        }
            return positions
        except Exception as e:
            print(f"⚠️ 获取现货持仓失败：{e}")
            return {}
    
    def get_positions(self):
        """获取持仓（合约/杠杆）"""
        try:
            data = self.request('GET', '/api/v5/account/positions')
            positions = {}
            for pos in data:
                symbol = pos.get('instId', '').replace('-USDT', '')
                if symbol:
                    # 辅助函数：安全转换 float
                    def safe_float(val, default=0.0):
                        if val is None or val == '':
                            return default
                        try:
                            return float(val)
                        except (ValueError, TypeError):
                            return default
                    
                    positions[symbol] = {
                        'side': 'LONG' if pos.get('posSide') == 'long' else 'SHORT',
                        'size': safe_float(pos.get('pos', 0)),
                        'entry_price': safe_float(pos.get('avgPx', 0)),
                        'current_price': safe_float(pos.get('last', 0)),
                        'pnl': safe_float(pos.get('upl', 0)),
                        'pnl_pct': safe_float(pos.get('uplRatio', 0))
                    }
            return positions
        except Exception as e:
            print(f"⚠️ 获取持仓失败：{e}")
            return {}
    
    def test_connection(self):
        """测试连接"""
        try:
            # 获取服务器时间
            data = self.request('GET', '/api/v5/public/time')
            if data:
                print(f"✅ OKX 连接成功，服务器时间：{data[0]}")
                return True
            return False
        except Exception as e:
            print(f"❌ OKX 连接失败：{e}")
            return False


# 测试
if __name__ == "__main__":
    print("=" * 50)
    print("OKX API 连接器测试")
    print("=" * 50)
    
    # 从配置文件读取
    config_file = '/Users/kelvin/.openclaw/workspace/skills/stock-market-pro/quant-trading-system/okx_config.json'
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        client = OKXClient(
            api_key=config['api_key'],
            secret_key=config['secret_key'],
            passphrase=config['passphrase'],
            testnet=config.get('testnet', True)
        )
        
        # 测试连接
        print("\n1️⃣ 测试连接...")
        if client.test_connection():
            print("✅ 连接成功")
        
        # 获取余额
        print("\n2️⃣ 获取余额...")
        balance = client.get_balance()
        print(f"   USDT 可用：{balance.get('USDT', 0):.2f}")
        print(f"   总权益：${balance.get('total_eq', 0):.2f}")
        
        # 获取行情
        print("\n3️⃣ 获取行情...")
        for symbol in ['BTC', 'ETH', 'SOL', 'XRP']:
            ticker = client.get_ticker(symbol)
            if ticker:
                print(f"   {symbol}: ${ticker['price']:.2f} (24h: ${ticker['volume_24h']:.0f})")
        
        # 获取 K 线
        print("\n4️⃣ 获取 K 线...")
        klines = client.get_klines('BTC', '15m', 10)
        if klines:
            print(f"   BTC 最新 K 线：${klines[-1]['close']:.2f}")
        
        print("\n" + "=" * 50)
        print("✅ OKX 测试完成")
        print("=" * 50)
        
    except FileNotFoundError:
        print(f"❌ 配置文件不存在：{config_file}")
        print("\n请创建配置文件，参考 okx_config.example.json")
    except Exception as e:
        print(f"❌ 测试失败：{e}")
