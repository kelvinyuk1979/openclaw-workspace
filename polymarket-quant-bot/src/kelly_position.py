#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
凯利公式仓位管理 [FRM-003]
计算最优下注比例，确保长期生存
"""

from typing import Optional

class KellyPosition:
    """凯利仓位管理器"""
    
    def __init__(self, fraction: float = 0.25):
        """
        初始化
        
        Args:
            fraction: 凯利分数，默认 0.25（1/4 凯利）
                       职业选手通常使用 1/4 到 1/2 倍凯利
        """
        self.fraction = fraction
    
    def calculate(self, win_prob: float, odds: float) -> float:
        """
        凯利公式计算最优下注比例
        
        公式：f* = (p × b - q) / b
        
        Args:
            win_prob: 获胜概率 p（0-1）
            odds: 赔率 b（每投入 1 美元赚取的净利润）
                   例如：赔率 2:1 → odds=2.0
                   Polymarket 价格 0.40 → odds=(1-0.40)/0.40=1.5
        
        Returns:
            最优下注比例（0-1）
        """
        if win_prob <= 0 or win_prob >= 1:
            return 0.0
        
        if odds <= 0:
            return 0.0
        
        lose_prob = 1 - win_prob
        
        # 凯利公式
        kelly = (win_prob * odds - lose_prob) / odds
        
        # 使用分数凯利，且不低于 0
        return max(kelly * self.fraction, 0.0)
    
    def position_size(self, bankroll: float, win_prob: float, odds: float,
                     max_position: Optional[float] = None) -> float:
        """
        计算具体下注金额
        
        Args:
            bankroll: 总资金
            win_prob: 获胜概率
            odds: 赔率
            max_position: 最大仓位比例（可选）
        
        Returns:
            下注金额
        """
        kelly_fraction = self.calculate(win_prob, odds)
        
        # 应用最大仓位限制
        if max_position:
            kelly_fraction = min(kelly_fraction, max_position)
        
        position = bankroll * kelly_fraction
        
        return position
    
    def calculate_odds_from_price(self, price: float) -> float:
        """
        从 Polymarket 价格计算赔率
        
        例如：价格 0.40 → 赔率 = (1-0.40)/0.40 = 1.5
        
        Args:
            price: Polymarket 价格（0-1）
        
        Returns:
            赔率
        """
        if price <= 0 or price >= 1:
            return 0.0
        
        return (1 - price) / price


def main():
    """测试函数"""
    print("\n" + "="*60)
    print("💰 凯利公式仓位计算器 - 测试")
    print("="*60)
    
    # 测试场景
    test_cases = [
        {'name': 'Fed cut Jun', 'win_prob': 0.62, 'price': 0.40},
        {'name': 'Trump OH', 'win_prob': 0.55, 'price': 0.52},
        {'name': 'Ceasefire 2024', 'win_prob': 0.58, 'price': 0.30},
        {'name': 'BTC 100K', 'win_prob': 0.70, 'price': 0.65},
    ]
    
    kelly = KellyPosition(fraction=0.25)  # 使用 1/4 凯利
    bankroll = 10000  # $10K 资金
    
    print(f"\n💵 总资金：${bankroll:,.0f}")
    print(f"📐 凯利分数：{kelly.fraction:.0%}（1/{int(1/kelly.fraction)} 凯利）\n")
    
    print(f"{'市场':<20} {'胜率':<8} {'价格':<8} {'赔率':<8} {'凯利%':<10} {'下注金额':<12}")
    print("-" * 70)
    
    for case in test_cases:
        odds = kelly.calculate_odds_from_price(case['price'])
        kelly_pct = kelly.calculate(case['win_prob'], odds)
        amount = kelly.position_size(bankroll, case['win_prob'], odds, max_position=0.10)
        
        print(f"{case['name']:<20} {case['win_prob']:<8.0%} {case['price']:<8.0%} "
              f"{odds:<8.2f} {kelly_pct:<10.1%} ${amount:<11,.0f}")
    
    print("\n" + "="*60)
    print("💡 提示：职业选手使用 1/4~1/2 凯利以避免爆仓风险")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
