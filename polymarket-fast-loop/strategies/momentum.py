#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动量交易策略
跟随趋势，突破交易
"""

import logging
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class TradeDecision:
    """交易决策"""
    action: str
    market_id: str
    price: float
    amount: float
    confidence: float
    reason: str


class MomentumStrategy:
    """
    动量策略
    
    规则：
    1. 计算价格变化率（动量）
    2. 当动量 > 阈值，跟随趋势买入
    3. 当动量反转，平仓离场
    4. 结合成交量确认信号
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.momentum_threshold = 0.05  # 5% 动量阈值
        self.volume_confirmation = 1.5  # 成交量放大 1.5 倍
        self.lookback_period = 5  # 看过去 5 个周期
        self.max_bet = config.get('trading', {}).get('max_bet', 100)
        
        # 价格历史缓存
        self.price_history: Dict[str, List[float]] = {}
        self.volume_history: Dict[str, List[float]] = {}
    
    def update_history(self, market_id: str, price: float, volume: float):
        """更新价格和成交量历史"""
        if market_id not in self.price_history:
            self.price_history[market_id] = []
            self.volume_history[market_id] = []
        
        self.price_history[market_id].append(price)
        self.volume_history[market_id].append(volume)
        
        # 保留最近 50 条数据
        max_len = 50
        if len(self.price_history[market_id]) > max_len:
            self.price_history[market_id] = self.price_history[market_id][-max_len:]
            self.volume_history[market_id] = self.volume_history[market_id][-max_len:]
    
    def calculate_momentum(self, prices: List[float]) -> float:
        """计算动量"""
        if len(prices) < self.lookback_period + 1:
            return 0.0
        
        current = prices[-1]
        previous = prices[-(self.lookback_period + 1)]
        
        if previous == 0:
            return 0.0
        
        return (current - previous) / previous
    
    def calculate_avg_volume(self, volumes: List[float]) -> float:
        """计算平均成交量"""
        if not volumes:
            return 0.0
        return sum(volumes) / len(volumes)
    
    def evaluate(self, market: Dict) -> Optional[TradeDecision]:
        """评估市场并生成交易决策"""
        market_id = market.get('id')
        yes_price = float(market.get('yesBid', 0))
        volume = float(market.get('volume', 0))
        
        # 更新历史数据
        self.update_history(market_id, yes_price, volume)
        
        prices = self.price_history.get(market_id, [])
        volumes = self.volume_history.get(market_id, [])
        
        # 数据不足
        if len(prices) < self.lookback_period + 1:
            return None
        
        # 计算动量
        momentum = self.calculate_momentum(prices)
        avg_volume = self.calculate_avg_volume(volumes[:-1]) if len(volumes) > 1 else volume
        
        # 成交量确认
        volume_confirmed = volume > avg_volume * self.volume_confirmation
        
        # 生成信号
        if momentum > self.momentum_threshold:
            # 正向动量，买入 YES
            confidence = min(0.5 + abs(momentum), 0.85)
            if volume_confirmed:
                confidence = min(confidence + 0.1, 0.95)
            
            return TradeDecision(
                action='buy_yes',
                market_id=market_id,
                price=yes_price,
                amount=self.max_bet * 0.5,
                confidence=confidence,
                reason=f'正向动量：{momentum:.2%}' + (' (成交量确认)' if volume_confirmed else '')
            )
        
        elif momentum < -self.momentum_threshold:
            # 负向动量，买入 NO
            confidence = min(0.5 + abs(momentum), 0.85)
            if volume_confirmed:
                confidence = min(confidence + 0.1, 0.95)
            
            return TradeDecision(
                action='buy_no',
                market_id=market_id,
                price=float(market.get('noBid', 0)),
                amount=self.max_bet * 0.5,
                confidence=confidence,
                reason=f'负向动量：{momentum:.2%}' + (' (成交量确认)' if volume_confirmed else '')
            )
        
        # 动量反转检测（平仓信号）
        if len(prices) > self.lookback_period * 2:
            prev_momentum = self.calculate_momentum(prices[:-self.lookback_period])
            
            # 动量反转
            if (momentum > 0 and prev_momentum < 0) or (momentum < 0 and prev_momentum > 0):
                if abs(momentum) < abs(prev_momentum) * 0.5:
                    return TradeDecision(
                        action='sell',
                        market_id=market_id,
                        price=yes_price,
                        amount=0,  # 全部平仓
                        confidence=0.7,
                        reason='动量反转，建议平仓'
                    )
        
        return None
    
    def batch_evaluate(self, markets: List[Dict]) -> List[TradeDecision]:
        """批量评估"""
        decisions = []
        for market in markets:
            decision = self.evaluate(market)
            if decision:
                decisions.append(decision)
        
        decisions.sort(key=lambda x: x.confidence, reverse=True)
        return decisions[:5]  # 只返回前 5 个最佳机会


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    config = {'trading': {'max_bet': 100}}
    strategy = MomentumStrategy(config)
    print("MomentumStrategy loaded")
