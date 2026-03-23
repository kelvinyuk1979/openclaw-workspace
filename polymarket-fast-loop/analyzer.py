#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polymarket 数据分析模块
技术指标、趋势分析、信号生成
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class MarketSignal:
    """交易信号"""
    market_id: str
    title: str
    signal_type: str  # 'buy_yes', 'buy_no', 'sell'
    confidence: float  # 0-1
    reason: str
    suggested_price: float
    suggested_amount: float


class PolymarketAnalyzer:
    """Polymarket 数据分析师"""
    
    def __init__(self):
        self.price_history: Dict[str, List[float]] = {}
    
    def update_price_history(self, market_id: str, price: float):
        """更新价格历史"""
        if market_id not in self.price_history:
            self.price_history[market_id] = []
        
        self.price_history[market_id].append(price)
        
        # 保留最近 100 条数据
        if len(self.price_history[market_id]) > 100:
            self.price_history[market_id] = self.price_history[market_id][-100:]
    
    def calculate_momentum(self, prices: List[float], period: int = 5) -> float:
        """计算动量指标"""
        if len(prices) < period + 1:
            return 0.0
        
        current = prices[-1]
        previous = prices[-(period + 1)]
        
        if previous == 0:
            return 0.0
        
        momentum = (current - previous) / previous
        return momentum
    
    def calculate_volatility(self, prices: List[float], period: int = 10) -> float:
        """计算波动率"""
        if len(prices) < period:
            return 0.0
        
        recent = prices[-period:]
        mean = sum(recent) / len(recent)
        variance = sum((p - mean) ** 2 for p in recent) / len(recent)
        
        return variance ** 0.5
    
    def calculate_fair_value(self, yes_price: float, no_price: float) -> float:
        """计算公平价值（套利机会检测）"""
        # 理论上 yes + no = 1
        # 如果有偏差，可能存在套利机会
        implied_prob = yes_price + no_price
        deviation = abs(implied_prob - 1.0)
        
        return {
            'fair_value': (yes_price + (1 - no_price)) / 2,
            'deviation': deviation,
            'arbitrage_opportunity': deviation > 0.02  # 2% 偏差阈值
        }
    
    def generate_signal(self, market: Dict, config: Dict) -> Optional[MarketSignal]:
        """
        生成交易信号
        
        策略：
        1. 动量策略 - 跟随价格趋势
        2. 均值回归 - 价格偏离公平价值时反向操作
        3. 套利策略 - 利用 yes/no 价差
        """
        market_id = market.get('id')
        yes_price = float(market.get('yesBid', 0))
        no_price = float(market.get('noBid', 0))
        volume = float(market.get('volume', 0))
        liquidity = float(market.get('liquidity', 0))
        
        # 更新价格历史
        self.update_price_history(market_id, yes_price)
        prices = self.price_history.get(market_id, [])
        
        # 基础筛选
        if volume < config.get('monitor', {}).get('volume_min', 1000):
            return None
        
        if liquidity < 500:  # 最小流动性
            return None
        
        # 计算指标
        momentum = self.calculate_momentum(prices) if len(prices) > 5 else 0
        volatility = self.calculate_volatility(prices) if len(prices) > 10 else 0
        fair_value = self.calculate_fair_value(yes_price, no_price)
        
        signal = None
        
        # 策略 1: 动量交易
        if abs(momentum) > 0.05:  # 5% 动量阈值
            if momentum > 0:
                signal = MarketSignal(
                    market_id=market_id,
                    title=market.get('title', ''),
                    signal_type='buy_yes',
                    confidence=min(0.5 + abs(momentum), 0.8),
                    reason=f"正向动量：{momentum:.2%}",
                    suggested_price=yes_price,
                    suggested_amount=config.get('trading', {}).get('max_bet', 100) * 0.5
                )
            else:
                signal = MarketSignal(
                    market_id=market_id,
                    title=market.get('title', ''),
                    signal_type='buy_no',
                    confidence=min(0.5 + abs(momentum), 0.8),
                    reason=f"负向动量：{momentum:.2%}",
                    suggested_price=no_price,
                    suggested_amount=config.get('trading', {}).get('max_bet', 100) * 0.5
                )
        
        # 策略 2: 套利机会
        if fair_value['arbitrage_opportunity']:
            # 选择更便宜的一侧
            if yes_price < (1 - no_price) - 0.02:
                signal = MarketSignal(
                    market_id=market_id,
                    title=market.get('title', ''),
                    signal_type='buy_yes',
                    confidence=0.7,
                    reason=f"套利机会：偏差 {fair_value['deviation']:.2%}",
                    suggested_price=yes_price,
                    suggested_amount=config.get('trading', {}).get('max_bet', 100) * 0.3
                )
            elif no_price < (1 - yes_price) - 0.02:
                signal = MarketSignal(
                    market_id=market_id,
                    title=market.get('title', ''),
                    signal_type='buy_no',
                    confidence=0.7,
                    reason=f"套利机会：偏差 {fair_value['deviation']:.2%}",
                    suggested_price=no_price,
                    suggested_amount=config.get('trading', {}).get('max_bet', 100) * 0.3
                )
        
        return signal
    
    def analyze_market(self, market: Dict) -> Dict:
        """分析单个市场"""
        yes_price = float(market.get('yesBid', 0))
        no_price = float(market.get('noBid', 0))
        
        return {
            'market_id': market.get('id'),
            'title': market.get('title'),
            'yes_price': yes_price,
            'no_price': no_price,
            'implied_probability': yes_price,
            'spread': abs(yes_price + no_price - 1),
            'volume': market.get('volume'),
            'liquidity': market.get('liquidity'),
        }


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    analyzer = PolymarketAnalyzer()
    print("Analyzer module loaded successfully")
