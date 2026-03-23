#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股数据获取模块 - 使用腾讯财经 API
数据源：http://qt.gtimg.cn/
"""

import requests
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class TencentStockData:
    """腾讯财经数据接口"""
    
    BASE_URL = "http://qt.gtimg.cn/q="
    SESSION_URL = "http://qt.gtimg.cn/r="
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://stockapp.finance.qq.com/',
        })
    
    def _convert_code(self, code: str) -> str:
        """转换股票代码格式
        600xxx -> sh600xxx
        000xxx -> sz000xxx
        300xxx -> sz300xxx
        """
        if code.startswith('6'):
            return f"sh{code}"
        elif code.startswith('0') or code.startswith('3'):
            return f"sz{code}"
        elif code.startswith('4') or code.startswith('8'):  # 北交所
            return f"bj{code}"
        else:
            return f"sz{code}"
    
    def get_realtime_quote(self, codes: List[str]) -> Dict:
        """获取实时行情数据
        
        Args:
            codes: 股票代码列表，如 ['600519', '000001']
        
        Returns:
            dict: {code: {price, change, volume, ...}}
        """
        # 转换代码格式
        qt_codes = [self._convert_code(c) for c in codes]
        code_str = ','.join(qt_codes)
        
        try:
            url = f"{self.SESSION_URL}{int(time.time()*1000)}&q={code_str}"
            response = self.session.get(url, timeout=self.timeout)
            response.encoding = 'gbk'  # 腾讯返回 GBK 编码
            
            data = {}
            for line in response.text.split('\n'):
                if not line.strip():
                    continue
                
                # 解析格式：v_sh600519="51~贵州茅台~600519~1468.00~..."
                match = re.search(r'v_(sh|sz|bj)(\d+)="([^"]+)"', line)
                if match:
                    prefix = match.group(1)
                    code = match.group(2)
                    values = match.group(3).split('~')
                    
                    if len(values) >= 50:
                        data[code] = {
                            'code': code,
                            'name': values[1],
                            'price': float(values[3]) if values[3] else 0,  # 当前价
                            'open': float(values[5]) if values[5] else 0,    # 开盘价
                            'high': float(values[33]) if values[33] else 0,  # 最高
                            'low': float(values[34]) if values[34] else 0,   # 最低
                            'close': float(values[4]) if values[4] else 0,   # 昨收
                            'volume': int(values[6]) if values[6] else 0,    # 成交量 (手)
                            'turnover': float(values[37]) if values[37] else 0,  # 成交额 (万元)
                            'change_pct': float(values[32]) if values[32] else 0,  # 涨跌幅%
                            'change': float(values[31]) if values[31] else 0,  # 涨跌额
                            'bid': float(values[11]) if values[11] else 0,   # 买一价
                            'ask': float(values[13]) if values[13] else 0,   # 卖一价
                            'bid_vol': int(values[10]) if values[10] else 0,  # 买一量
                            'ask_vol': int(values[12]) if values[12] else 0,  # 卖一量
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        }
            
            return data
            
        except Exception as e:
            print(f"❌ 获取行情失败：{e}")
            return {}
    
    def get_historical_data(self, code: str, days: int = 60) -> Optional[List[Dict]]:
        """获取历史 K 线数据（日线）
        
        使用腾讯财经日 K 接口
        """
        qt_code = self._convert_code(code)
        
        try:
            # 腾讯日 K 接口
            url = f"http://data.gtimg.cn/flashdata/hushen/minute/{qt_code}.js"
            params = {
                'maxcnt': days,
                'type': 'qfq',  # 前复权
                '_': int(time.time() * 1000)
            }
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.encoding = 'gbk'
            
            # 解析格式：day_~20260317~1468.00~1480.00~1450.00~1460.00~123456
            data = []
            for line in response.text.split('\n'):
                if line.startswith('day_'):
                    parts = line.split('~')[1:]  # 跳过 day_
                    if len(parts) >= 6:
                        try:
                            data.append({
                                'date': parts[0],
                                'open': float(parts[1]),
                                'high': float(parts[2]),
                                'low': float(parts[3]),
                                'close': float(parts[4]),
                                'volume': int(parts[5]),
                            })
                        except (ValueError, IndexError):
                            continue
            
            return data[:days] if data else None
            
        except Exception as e:
            print(f"❌ 获取历史数据失败 ({code}): {e}")
            return None
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """计算 RSI 指标"""
        if len(prices) < period + 1:
            return 50.0
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    def calculate_ma(self, prices: List[float], period: int = 5) -> float:
        """计算移动平均线"""
        if len(prices) < period:
            return prices[-1] if prices else 0
        
        return round(sum(prices[-period:]) / period, 2)


class EastMoneyData:
    """东方财富数据接口（备用）"""
    
    BASE_URL = "http://push2.eastmoney.com/api/qt/stock/get"
    KLINE_URL = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
    
    def _convert_code(self, code: str) -> str:
        """转换东方财富代码格式"""
        if code.startswith('6'):
            return f"1.{code}"  # 沪市
        elif code.startswith('0') or code.startswith('3'):
            return f"0.{code}"  # 深市
        elif code.startswith('4') or code.startswith('8'):
            return f"0.{code}"  # 北交所
        else:
            return f"0.{code}"
    
    def get_realtime_quote(self, codes: List[str]) -> Dict:
        """获取实时行情"""
        data = {}
        
        for code in codes:
            secid = self._convert_code(code)
            try:
                url = f"{self.BASE_URL}?secid={secid}&fields=f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f53,f54,f55,f56,f57,f58,f84,f85,f86,f87,f117,f118,f119,f120,f121,f122,f123,f124,f125,f126,f127,f128,f129,f130,f131,f132,f133,f134,f135,f136,f137,f138,f139,f140,f141,f142,f143,f144,f145,f146,f147,f148,f149,f150,f151,f152,f153,f154,f155,f156,f157,f158,f159,f160,f161,f162,f163,f164,f165,f166,f167,f168,f169,f170,f171,f172,f173,f174,f175,f176,f177,f178,f179,f180,f181,f182,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f193,f194,f195,f196,f197,f198,f199,f200"
                response = self.session.get(url, timeout=self.timeout)
                result = response.json()
                
                if result.get('data'):
                    d = result['data']
                    data[code] = {
                        'code': code,
                        'name': d.get('f58', ''),
                        'price': d.get('f43', 0) / 100,  # 价格单位是分
                        'open': d.get('f46', 0) / 100,
                        'high': d.get('f44', 0) / 100,
                        'low': d.get('f45', 0) / 100,
                        'close': d.get('f60', 0) / 100,  # 昨收
                        'volume': d.get('f47', 0),
                        'turnover': d.get('f48', 0),
                        'change_pct': d.get('f170', 0) / 100,  # 涨跌幅%
                        'change': d.get('f169', 0) / 100,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    }
                
                time.sleep(0.1)  # 避免请求过快
                
            except Exception as e:
                print(f"❌ 东方财富获取失败 ({code}): {e}")
        
        return data


def test_data_sources():
    """测试数据源"""
    print("\n" + "="*60)
    print("🧪 测试 A 股数据源")
    print("="*60)
    
    test_codes = ['600519', '300750', '002594', '000858', '601318']
    
    # 测试腾讯财经
    print("\n1️⃣ 腾讯财经 API:")
    tencent = TencentStockData()
    data = tencent.get_realtime_quote(test_codes)
    
    if data:
        print(f"   ✅ 获取成功 {len(data)} 只股票")
        for code, d in list(data.items())[:3]:
            print(f"   - {code} {d['name']}: ¥{d['price']:.2f} ({d['change_pct']:+.2f}%)")
    else:
        print("   ❌ 获取失败")
    
    # 测试东方财富
    print("\n2️⃣ 东方财富 API:")
    eastmoney = EastMoneyData()
    data = eastmoney.get_realtime_quote(test_codes)
    
    if data:
        print(f"   ✅ 获取成功 {len(data)} 只股票")
        for code, d in list(data.items())[:3]:
            print(f"   - {code} {d['name']}: ¥{d['price']:.2f} ({d['change_pct']:+.2f}%)")
    else:
        print("   ❌ 获取失败")
    
    # 测试历史数据
    print("\n3️⃣ 腾讯历史 K 线:")
    tencent = TencentStockData()
    hist = tencent.get_historical_data('600519', days=30)
    
    if hist:
        print(f"   ✅ 获取成功 {len(hist)} 天数据")
        if hist:
            latest = hist[0]
            print(f"   - 最新：{latest['date']} 开{latest['open']} 收{latest['close']} 高{latest['high']} 低{latest['low']}")
            
            # 计算 RSI
            closes = [d['close'] for d in hist]
            rsi = tencent.calculate_rsi(closes)
            ma5 = tencent.calculate_ma(closes, 5)
            ma20 = tencent.calculate_ma(closes, 20)
            print(f"   - RSI(14): {rsi:.2f}, MA5: {ma5:.2f}, MA20: {ma20:.2f}")
    else:
        print("   ❌ 获取失败")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    test_data_sources()
