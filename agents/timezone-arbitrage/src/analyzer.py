#!/usr/bin/env python3
"""
Edge 计算器 - 计算套利机会的预期收益

核心公式：
Edge = (真实概率 - 市场价格) / 市场价格
"""

from typing import Dict, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger('timezone-arbitrage.analyzer')


class EdgeAnalyzer:
    """Edge 分析器"""
    
    def __init__(self, config: dict):
        self.config = config
    
    def calculate_edge(self, signal: dict) -> dict:
        """
        计算单个信号的 Edge
        
        Args:
            signal: 信息源信号，包含：
                - market_name: 市场名称
                - true_probability: 真实概率 (0-1)
                - market_price: Polymarket 价格 (0-1)
                - settlement_time: 结算时间
                - confidence: 置信度
        
        Returns:
            edge_data: 包含 Edge 计算结果和所需资金
        """
        true_prob = signal['true_probability']
        market_price = signal['market_price']
        confidence = signal.get('confidence', 0.8)
        
        # 计算 Edge
        edge_percent = ((true_prob - market_price) / market_price) * 100
        
        # 应用置信度调整
        adjusted_edge = edge_percent * confidence
        
        # 计算结算窗口
        settlement_time = signal['settlement_time']
        now = datetime.utcnow()
        settlement_minutes = (settlement_time - now).total_seconds() / 60
        
        # 计算最优仓位
        max_capital = self.config['trading']['max_capital_per_trade']
        position_size = self._calculate_position_size(
            adjusted_edge,
            settlement_minutes,
            max_capital
        )
        
        # 计算预期回报
        expected_return = position_size * (true_prob / market_price - 1)
        
        return {
            'market_name': signal['market_name'],
            'true_probability': true_prob,
            'market_price': market_price,
            'edge_percent': edge_percent,
            'adjusted_edge': adjusted_edge,
            'confidence': confidence,
            'settlement_minutes': settlement_minutes,
            'required_capital': position_size,
            'expected_return': expected_return,
            'risk_reward_ratio': expected_return / position_size if position_size > 0 else 0
        }
    
    def _calculate_position_size(self, edge: float, settlement_minutes: float, max_capital: float) -> float:
        """
        计算最优仓位大小
        
        基于 Kelly 公式的简化版本：
        f* = (p * b - q) / b
        
        其中：
        - p = 获胜概率
        - q = 失败概率 (1-p)
        - b = 赔率
        """
        # 基础 Kelly 比例
        kelly_percent = min(edge / 100, 0.25)  # 最大不超过 25%
        
        # 根据结算窗口调整（时间越短，仓位越大）
        time_factor = min(90 / settlement_minutes, 2.0) if settlement_minutes > 0 else 1.0
        
        # 计算最终仓位
        position_size = max_capital * kelly_percent * time_factor
        
        # 应用仓位限制
        min_position = self.config['trading']['position_sizing']['min_position_size']
        max_position = self.config['trading']['position_sizing']['max_position_size']
        
        position_size = max(min_position, min(position_size, max_position))
        
        return round(position_size, 2)
    
    def calculate_portfolio_metrics(self, opportunities: List[dict]) -> dict:
        """
        计算投资组合的整体指标
        
        Args:
            opportunities: 机会列表（包含 edge 数据）
        
        Returns:
            metrics: 投资组合指标
        """
        if not opportunities:
            return {}
        
        total_capital = sum(opp['edge']['required_capital'] for opp in opportunities)
        total_expected_return = sum(opp['edge']['expected_return'] for opp in opportunities)
        
        # 加权平均 Edge
        weighted_edge = sum(
            opp['edge']['adjusted_edge'] * opp['edge']['required_capital']
            for opp in opportunities
        ) / total_capital if total_capital > 0 else 0
        
        # 平均结算时间
        avg_settlement = sum(opp['edge']['settlement_minutes'] for opp in opportunities) / len(opportunities)
        
        # 风险分散度（市场数量）
        diversification = len(opportunities)
        
        return {
            'total_capital': total_capital,
            'total_expected_return': total_expected_return,
            'total_roi_percent': (total_expected_return / total_capital * 100) if total_capital > 0 else 0,
            'weighted_edge': weighted_edge,
            'avg_settlement_minutes': avg_settlement,
            'diversification': diversification,
            'sharpe_ratio': self._calculate_sharpe(opportunities)
        }
    
    def _calculate_sharpe(self, opportunities: List[dict]) -> float:
        """
        计算简化的夏普比率
        
        假设无风险利率为 0
        """
        if not opportunities:
            return 0
        
        returns = [opp['edge']['risk_reward_ratio'] for opp in opportunities]
        avg_return = sum(returns) / len(returns)
        
        # 标准差
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        std_dev = variance ** 0.5
        
        return avg_return / std_dev if std_dev > 0 else 0
