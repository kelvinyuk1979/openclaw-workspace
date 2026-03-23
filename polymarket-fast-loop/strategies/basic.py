#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础交易策略
低买高卖，简单有效
"""

import logging
from typing import Dict, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TradeDecision:
    """交易决策"""
    action: str  # 'buy_yes', 'buy_no', 'hold', 'sell'
    market_id: str
    price: float
    amount: float
    confidence: float
    reason: str


class BasicStrategy:
    """
    基础策略
    
    规则：
    1. 当 YES 价格 < 0.3 时，考虑买入 YES（便宜）
    2. 当 YES 价格 > 0.7 时，考虑买入 NO（NO 便宜）
    3. 当持仓盈利 > 止盈时，卖出
    4. 当持仓亏损 < 止损时，卖出
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.buy_low_threshold = 0.3
        self.buy_high_threshold = 0.7
        self.min_volume = config.get('monitor', {}).get('volume_min', 1000)
        self.max_bet = config.get('trading', {}).get('max_bet', 100)
    
    def evaluate(self, market: Dict, position: Optional[Dict] = None) -> TradeDecision:
        """评估市场并生成交易决策"""
        market_id = market.get('id')
        yes_price = float(market.get('yesBid', 0))
        no_price = float(market.get('noBid', 0))
        volume = float(market.get('volume', 0))
        liquidity = float(market.get('liquidity', 0))
        
        # 基础筛选
        if volume < self.min_volume:
            return TradeDecision(
                action='hold',
                market_id=market_id,
                price=0,
                amount=0,
                confidence=0,
                reason='交易量不足'
            )
        
        if liquidity < 500:
            return TradeDecision(
                action='hold',
                market_id=market_id,
                price=0,
                amount=0,
                confidence=0,
                reason='流动性不足'
            )
        
        # 检查现有持仓
        if position:
            pnl_percent = position.get('pnl_percent', 0)
            stop_loss = self.config.get('trading', {}).get('stop_loss', 0.2)
            take_profit = self.config.get('trading', {}).get('take_profit', 0.5)
            
            if pnl_percent <= -stop_loss:
                return TradeDecision(
                    action='sell',
                    market_id=market_id,
                    price=yes_price,
                    amount=position.get('shares', 0),
                    confidence=0.9,
                    reason=f'触发止损：{pnl_percent:.2%}'
                )
            
            if pnl_percent >= take_profit:
                return TradeDecision(
                    action='sell',
                    market_id=market_id,
                    price=yes_price,
                    amount=position.get('shares', 0),
                    confidence=0.9,
                    reason=f'触发止盈：{pnl_percent:.2%}'
                )
        
        # 开仓逻辑
        if yes_price < self.buy_low_threshold:
            # YES 便宜，买入 YES
            amount = self.max_bet * 0.5  # 半仓
            return TradeDecision(
                action='buy_yes',
                market_id=market_id,
                price=yes_price,
                amount=amount,
                confidence=0.6 + (self.buy_low_threshold - yes_price),
                reason=f'低价买入 YES: {yes_price:.3f}'
            )
        
        elif yes_price > self.buy_high_threshold:
            # YES 贵，买入 NO
            amount = self.max_bet * 0.5
            return TradeDecision(
                action='buy_no',
                market_id=market_id,
                price=no_price,
                amount=amount,
                confidence=0.6 + (yes_price - self.buy_high_threshold),
                reason=f'高价买入 NO: {no_price:.3f}'
            )
        
        # 持有
        return TradeDecision(
            action='hold',
            market_id=market_id,
            price=0,
            amount=0,
            confidence=0,
            reason='无明确信号'
        )
    
    def batch_evaluate(self, markets: List[Dict], positions: Dict[str, Dict]) -> List[TradeDecision]:
        """批量评估多个市场"""
        decisions = []
        for market in markets:
            market_id = market.get('id')
            position = positions.get(market_id)
            decision = self.evaluate(market, position)
            
            if decision.action != 'hold':
                decisions.append(decision)
        
        # 按置信度排序
        decisions.sort(key=lambda x: x.confidence, reverse=True)
        return decisions


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    config = {'trading': {'max_bet': 100, 'stop_loss': 0.2, 'take_profit': 0.5}}
    strategy = BasicStrategy(config)
    print("BasicStrategy loaded")
