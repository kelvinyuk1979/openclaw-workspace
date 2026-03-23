#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polymarket 天气交易策略
基于 NWS 天气预报 vs 市场定价的套利策略
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class WeatherSignal:
    """天气交易信号"""
    city: str
    date: str
    forecast_temp: int
    market_bucket: str
    market_price: float
    signal_type: str  # 'buy_yes' or 'buy_no'
    confidence: float
    expected_value: float
    position_size: float
    reason: str


class WeatherStrategy:
    """
    天气交易策略
    
    逻辑：
    1. NWS 预报明天纽约最高温 46°F
    2. Polymarket 市场 "46-47°F 桶" 定价 8¢
    3. 市场低估 → 买入 YES
    4. 价格涨到 45¢ → 卖出锁定利润
    """
    
    def __init__(self, config: Dict):
        self.config = config
        
        # 交易阈值
        self.entry_threshold = config.get('entry_threshold', 0.15)  # 15¢ 买入
        self.exit_threshold = config.get('exit_threshold', 0.45)    # 45¢ 卖出
        self.max_position = config.get('max_position', 0.05)         # 单笔最大 5%
        self.min_confidence = config.get('min_confidence', 0.60)     # 最小置信度
        
        # 温度桶容差（°F）
        self.temp_tolerance = config.get('temp_tolerance', 2)
    
    def parse_temperature_bucket(self, bucket_name: str) -> Tuple[int, int]:
        """
        解析温度桶名称为数字范围
        
        示例：
        "46-47°F" → (46, 47)
        "48°F or higher" → (48, 999)
        "40°F or lower" → (-999, 40)
        """
        try:
            # 清理字符串
            bucket = bucket_name.lower().replace('°f', '').replace('f', '').strip()
            
            # 处理 "X or higher"
            if 'or higher' in bucket or 'above' in bucket:
                temp = int(''.join(filter(str.isdigit, bucket.split('or')[0])))
                return (temp, 999)
            
            # 处理 "X or lower"
            if 'or lower' in bucket or 'below' in bucket:
                temp = int(''.join(filter(str.isdigit, bucket.split('or')[0])))
                return (-999, temp)
            
            # 处理 "X-Y"
            if '-' in bucket:
                parts = bucket.split('-')
                low = int(''.join(filter(str.isdigit, parts[0])))
                high = int(''.join(filter(str.isdigit, parts[1])))
                return (low, high)
            
            # 单个温度值
            temp = int(''.join(filter(str.isdigit, bucket)))
            return (temp, temp + 1)
            
        except Exception as e:
            logger.debug(f"解析温度桶失败：{bucket_name}, 错误：{e}")
            return (0, 0)
    
    def is_temp_in_bucket(self, forecast_temp: int, bucket_range: Tuple[int, int]) -> bool:
        """检查预报温度是否在桶范围内"""
        low, high = bucket_range
        if high == 999:
            return forecast_temp >= low
        elif low == -999:
            return forecast_temp <= high
        else:
            return low <= forecast_temp <= high
    
    def calculate_expected_value(self, forecast_temp: int, bucket_range: Tuple[int, int], 
                                  market_price: float) -> float:
        """
        计算期望值
        
        基于 NWS 预报准确率（约 75-85%）和历史偏差调整
        """
        # 基础概率：NWS 预报准确率
        base_probability = 0.75
        
        # 温度容差调整：预报温度离桶边界越远，置信度越高
        low, high = bucket_range
        if low != -999 and high != 999:
            bucket_mid = (low + high) / 2
            distance_from_mid = abs(forecast_temp - bucket_mid)
            
            # 每偏离 1°F，降低 5% 置信度
            tolerance_adjustment = max(0, 1 - distance_from_mid * 0.05)
        else:
            tolerance_adjustment = 1.0
        
        # 计算调整后概率
        adjusted_probability = base_probability * tolerance_adjustment
        
        # 期望值 = (概率 × 赔付) - 成本
        # Polymarket 赔付 = 1 - 价格
        payout = 1.0 - market_price
        expected_value = (adjusted_probability * payout) - ((1 - adjusted_probability) * market_price)
        
        return expected_value
    
    def generate_signals(self, forecast_data: List[Dict], market_data: List[Dict], 
                         balance: float = 1000.0) -> List[WeatherSignal]:
        """
        生成交易信号
        
        Args:
            forecast_data: NWS 天气预报数据
            market_data: Polymarket 市场数据
            balance: 账户余额
        
        Returns:
            交易信号列表
        """
        signals = []
        
        for forecast in forecast_data:
            forecast_temp = forecast['high_temp_f']
            forecast_date = forecast['date']
            city = forecast['location']
            
            # 查找对应市场
            matching_market = self._find_matching_market(forecast_date, city, market_data)
            
            if not matching_market:
                logger.debug(f"未找到 {city} {forecast_date} 的市场")
                continue
            
            # 解析市场桶
            bucket_name = matching_market.get('title', '')
            bucket_range = self.parse_temperature_bucket(bucket_name)
            
            if bucket_range == (0, 0):
                continue
            
            # 检查预报是否在桶内
            in_bucket = self.is_temp_in_bucket(forecast_temp, bucket_range)
            
            if not in_bucket:
                continue
            
            # 获取市场价格
            market_price = matching_market.get('yesBid', 0.5)
            
            # 检查是否低于入场阈值
            if market_price >= self.entry_threshold:
                continue
            
            # 计算期望值
            ev = self.calculate_expected_value(forecast_temp, bucket_range, market_price)
            
            # 计算置信度
            confidence = min(0.95, 0.60 + abs(self.entry_threshold - market_price))
            
            if confidence < self.min_confidence:
                continue
            
            # 计算仓位大小
            position_size = balance * self.max_position
            
            # 生成信号
            signal = WeatherSignal(
                city=city,
                date=forecast_date,
                forecast_temp=forecast_temp,
                market_bucket=bucket_name,
                market_price=market_price,
                signal_type='buy_yes',
                confidence=confidence,
                expected_value=ev,
                position_size=position_size,
                reason=f"NWS 预报 {forecast_temp}°F，市场定价 {market_price:.2f}¢ (EV: {ev:.3f})"
            )
            
            signals.append(signal)
            logger.info(f"🎯 发现信号：{city} {forecast_date} - {bucket_name} @ {market_price:.2f}¢")
        
        # 按置信度排序
        signals.sort(key=lambda x: x.confidence, reverse=True)
        
        return signals
    
    def _find_matching_market(self, forecast_date: str, city: str, 
                               market_data: List[Dict]) -> Optional[Dict]:
        """查找匹配的市场"""
        # 解析日期
        try:
            target_date = datetime.strptime(forecast_date, '%Y-%m-%d')
            date_str = target_date.strftime('%B %d').lower()  # "march 14"
        except:
            return None
        
        # 城市映射
        city_mapping = {
            'New York LaGuardia': ['new york', 'ny', 'nyc'],
            'Dallas Love Field': ['dallas', 'tx'],
            'Chicago O\'Hare': ['chicago', 'il'],
            'Los Angeles Intl': ['los angeles', 'la'],
            'Miami Intl': ['miami', 'fl'],
            'Boston Logan': ['boston', 'ma'],
            'Denver Intl': ['denver', 'co'],
            'Atlanta Hartsfield': ['atlanta', 'ga']
        }
        
        city_keywords = city_mapping.get(city, [city.lower()])
        
        for market in market_data:
            title = market.get('title', '').lower()
            
            # 检查日期
            if date_str not in title:
                continue
            
            # 检查城市
            if any(keyword in title for keyword in city_keywords):
                # 检查是否是温度市场
                if 'temperature' in title or '°f' in title or 'high' in title:
                    return market
        
        return None
    
    def should_exit(self, current_price: float, entry_price: float) -> bool:
        """检查是否应该平仓"""
        # 达到止盈阈值
        if current_price >= self.exit_threshold:
            return True
        
        # 止损：价格下跌 50%
        if current_price <= entry_price * 0.5:
            return True
        
        return False


def test_strategy():
    """测试策略"""
    logger.info("🧪 测试天气策略...")
    
    config = {
        'entry_threshold': 0.15,
        'exit_threshold': 0.45,
        'max_position': 0.05,
        'min_confidence': 0.60
    }
    
    strategy = WeatherStrategy(config)
    
    # 测试温度桶解析
    test_buckets = [
        "46-47°F",
        "48°F or higher",
        "40°F or lower",
        "50-52°F"
    ]
    
    logger.info("\n温度桶解析测试:")
    for bucket in test_buckets:
        result = strategy.parse_temperature_bucket(bucket)
        logger.info(f"  {bucket:20s} → {result}")
    
    # 测试温度检查
    logger.info("\n温度检查测试:")
    test_cases = [
        (46, (45, 47), True),
        (48, (45, 47), False),
        (50, (48, 999), True),
        (45, (48, 999), False),
    ]
    
    for temp, bucket, expected in test_cases:
        result = strategy.is_temp_in_bucket(temp, bucket)
        status = "✅" if result == expected else "❌"
        logger.info(f"  {status} {temp}°F in {bucket} → {result}")
    
    return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_strategy()
