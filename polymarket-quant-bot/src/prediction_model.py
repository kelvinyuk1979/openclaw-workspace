#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
预测模型模块
整合多因子生成市场事件的真实概率预测
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

class PredictionModel:
    """多因子预测模型"""
    
    def __init__(self):
        """初始化模型"""
        # 因子权重（可通过回测优化）
        self.weights = {
            'base_rate': 0.30,      # 基础率权重 30%
            'market_sentiment': 0.20,  # 市场情绪 20%
            'momentum': 0.15,       # 动量因子 15%
            'volume_signal': 0.15,  # 交易量信号 15%
            'news_catalyst': 0.20,  # 新闻催化剂 20%
        }
        
        # 基础率数据库（扩展版）
        self.base_rates = {
            # 政治类
            'politics_incumbent': 0.75,
            'politics_challenger': 0.35,
            'politics_approval_high': 0.82,
            'politics_approval_low': 0.28,
            
            # 经济类
            'economics_rate_cut': 0.65,
            'economics_rate_hold': 0.70,
            'economics_recession': 0.25,
            
            # 加密货币类
            'crypto_bull_market': 0.60,
            'crypto_bear_market': 0.30,
            'crypto_etf_approval': 0.65,
            'crypto_price_target': 0.55,
            
            # 地缘政治类
            'geopolitics_ceasefire': 0.40,
            'geopolitics_escalation': 0.35,
            'geopolitics_election': 0.50,
            
            # 体育类
            'sports_home_win': 0.58,
            'sports_favorite': 0.65,
        }
    
    def predict(self, market_data: Dict, historical_data: List[Dict] = None) -> Tuple[float, Dict]:
        """
        综合预测
        
        Args:
            market_data: 市场数据
                {
                    'id': str,
                    'category': str,
                    'yes_price': float,
                    'volume_24h': float,
                    'open_interest': float,
                    'question': str
                }
            historical_data: 历史价格数据（可选）
        
        Returns:
            (predicted_prob, factor_breakdown)
            - predicted_prob: 预测概率
            - factor_breakdown: 各因子贡献
        """
        factors = {}
        
        # 1. 基础率因子
        base_rate_prob = self._calculate_base_rate(market_data)
        factors['base_rate'] = base_rate_prob
        
        # 2. 市场情绪因子
        sentiment_prob = self._calculate_sentiment(market_data)
        factors['market_sentiment'] = sentiment_prob
        
        # 3. 动量因子
        momentum_prob = self._calculate_momentum(market_data, historical_data)
        factors['momentum'] = momentum_prob
        
        # 4. 交易量因子
        volume_prob = self._calculate_volume_signal(market_data)
        factors['volume_signal'] = volume_prob
        
        # 5. 新闻催化剂因子
        news_prob = self._calculate_news_catalyst(market_data)
        factors['news_catalyst'] = news_prob
        
        # 加权平均
        predicted_prob = sum(
            factors[k] * self.weights[k]
            for k in self.weights.keys()
        )
        
        # 限制在 0-1 范围
        predicted_prob = max(0.0, min(1.0, predicted_prob))
        
        return predicted_prob, factors
    
    def _calculate_base_rate(self, market_data: Dict) -> float:
        """
        基础率因子
        
        根据市场分类和历史统计计算基础概率
        """
        category = market_data.get('category', 'unknown')
        question = market_data.get('question', '').lower()
        
        # 根据关键词匹配基础率
        base_rate = 0.50  # 默认 50%
        
        # 政治类
        if category == 'politics':
            if 'incumbent' in question or 'current' in question:
                base_rate = self.base_rates['politics_incumbent']
            elif 'challenger' in question:
                base_rate = self.base_rates['politics_challenger']
            elif 'approval' in question and 'high' in question:
                base_rate = self.base_rates['politics_approval_high']
        
        # 经济类
        elif category == 'economics':
            if 'cut' in question or 'lower' in question:
                base_rate = self.base_rates['economics_rate_cut']
            elif 'hold' in question or 'unchanged' in question:
                base_rate = self.base_rates['economics_rate_hold']
            elif 'recession' in question:
                base_rate = self.base_rates['economics_recession']
        
        # 加密货币类
        elif category == 'crypto':
            if 'etf' in question:
                base_rate = self.base_rates['crypto_etf_approval']
            elif '100k' in question or 'price' in question:
                base_rate = self.base_rates['crypto_price_target']
            elif 'bull' in question:
                base_rate = self.base_rates['crypto_bull_market']
        
        # 地缘政治类
        elif category == 'geopolitics':
            if 'ceasefire' in question or 'peace' in question:
                base_rate = self.base_rates['geopolitics_ceasefire']
            elif 'escalation' in question or 'war' in question:
                base_rate = self.base_rates['geopolitics_escalation']
        
        return base_rate
    
    def _calculate_sentiment(self, market_data: Dict) -> float:
        """
        市场情绪因子
        
        根据市场价格和未平仓合约推断市场情绪
        """
        yes_price = market_data.get('yes_price', 0.5)
        open_interest = market_data.get('open_interest', 0)
        
        # 高未平仓合约 + 高价格 = 强烈看涨情绪
        # 高未平仓合约 + 低价格 = 强烈看跌情绪
        
        # 基础情绪（从价格推导）
        sentiment = yes_price
        
        # 未平仓合约调整（高 OI 增强信号）
        oi_factor = 1.0
        if open_interest > 1000000:  # >100 万
            oi_factor = 1.1
        elif open_interest > 500000:
            oi_factor = 1.05
        elif open_interest < 100000:
            oi_factor = 0.95
        
        sentiment = sentiment * oi_factor
        
        # 限制在 0-1
        return max(0.0, min(1.0, sentiment))
    
    def _calculate_momentum(self, market_data: Dict, 
                           historical_data: List[Dict] = None) -> float:
        """
        动量因子
        
        如果有历史数据，计算价格趋势
        """
        if not historical_data or len(historical_data) < 2:
            # 无历史数据，返回中性值
            return 0.50
        
        # 计算近期动量（简单示例）
        recent_prices = [d['yes_price'] for d in historical_data[-5:]]
        
        if len(recent_prices) < 2:
            return 0.50
        
        # 价格变化率
        price_change = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
        
        # 转换为概率调整
        # 正动量 → 概率上调，负动量 → 概率下调
        momentum_adjustment = price_change * 0.5
        
        current_price = market_data.get('yes_price', 0.5)
        momentum_prob = current_price + momentum_adjustment
        
        return max(0.0, min(1.0, momentum_prob))
    
    def _calculate_volume_signal(self, market_data: Dict) -> float:
        """
        交易量因子
        
        异常放量通常预示信息优势方入场
        """
        volume_24h = market_data.get('volume_24h', 0)
        open_interest = market_data.get('open_interest', 1)
        
        # 成交量/未平仓比
        vol_oi_ratio = volume_24h / max(open_interest, 1)
        
        # 高比率（>0.5）表示活跃交易，可能有新信息
        if vol_oi_ratio > 0.5:
            # 放量，增强当前价格信号
            return market_data.get('yes_price', 0.5) * 1.05
        elif vol_oi_ratio < 0.1:
            # 缩量，信号减弱，回归均值
            return 0.50
        else:
            # 正常
            return market_data.get('yes_price', 0.5)
    
    def _calculate_news_catalyst(self, market_data: Dict) -> float:
        """
        新闻催化剂因子
        
        根据近期新闻调整概率
        实际应用中应接入新闻 API
        """
        # 简化版：根据市场分类给默认值
        category = market_data.get('category', 'unknown')
        
        news_map = {
            'politics': 0.55,      # 政治市场通常有新闻驱动
            'economics': 0.60,     # 经济数据发布频繁
            'crypto': 0.65,        # 加密货币新闻密集
            'geopolitics': 0.50,   # 地缘政治不确定性高
            'sports': 0.45,        # 体育相对稳定
        }
        
        return news_map.get(category, 0.50)
    
    def calculate_ev(self, market_data: Dict) -> Tuple[float, float, Dict]:
        """
        计算期望值
        
        Args:
            market_data: 市场数据
        
        Returns:
            (market_price, predicted_prob, ev, factors)
        """
        market_price = market_data.get('yes_price', 0.5)
        predicted_prob, factors = self.predict(market_data)
        
        # EV = (predicted_prob - market_price) / market_price
        ev = (predicted_prob - market_price) / market_price if market_price > 0 else 0
        
        return market_price, predicted_prob, ev, factors


def main():
    """测试函数"""
    print("\n" + "="*60)
    print("🧠 预测模型 - 测试")
    print("="*60)
    
    model = PredictionModel()
    
    # 测试市场
    test_markets = [
        {
            'id': 'fed-cut-jun-2026',
            'category': 'economics',
            'yes_price': 0.40,
            'volume_24h': 125000,
            'open_interest': 450000,
            'question': 'Will the Fed cut rates in June 2026?'
        },
        {
            'id': 'btc-100k-2026',
            'category': 'crypto',
            'yes_price': 0.65,
            'volume_24h': 520000,
            'open_interest': 1200000,
            'question': 'Will BTC reach $100K in 2026?'
        },
        {
            'id': 'ceasefire-2024',
            'category': 'geopolitics',
            'yes_price': 0.30,
            'volume_24h': 250000,
            'open_interest': 680000,
            'question': 'Will there be a ceasefire in 2024?'
        },
    ]
    
    print("\n📊 预测结果：\n")
    print(f"{'市场':<25} {'市场价':<10} {'预测价':<10} {'EV':<10} {'信号':<8}")
    print("-" * 70)
    
    for m in test_markets:
        market_price, pred_prob, ev, factors = model.calculate_ev(m)
        
        signal = 'BUY' if ev > 0.05 else 'SELL' if ev < -0.05 else 'SKIP'
        
        print(f"{m['id']:<25} {market_price:<10.0%} {pred_prob:<10.0%} "
              f"{ev:<+10.1%} {signal:<8}")
        
        # 显示因子分解
        print(f"  因子分解:")
        for factor, value in factors.items():
            weight = model.weights[factor]
            print(f"    {factor:<20}: {value:.0%} × {weight:.0%} = {value*weight:.1%}")
        print()
    
    print("="*60)
    print("💡 提示：可通过回测优化因子权重")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
