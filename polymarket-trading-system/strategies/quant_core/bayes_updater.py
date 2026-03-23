#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
贝叶斯更新引擎 [FRM-002]
根据新信息动态更新概率，避免锚定效应
"""

from typing import List, Tuple, Dict

class BayesUpdater:
    """贝叶斯概率更新器"""
    
    def __init__(self):
        """初始化"""
        pass
    
    def update(self, prior: float, likelihood_true: float, 
               likelihood_false: float) -> float:
        """
        单次贝叶斯更新
        
        公式：P(H|E) = P(E|H) × P(H) / [P(E|H) × P(H) + P(E|¬H) × (1-P(H))]
        
        Args:
            prior: 先验概率 P(H)
            likelihood_true: 似然度 P(E|H) - 如果假设成立，观察到该证据的可能性
            likelihood_false: 似然度 P(E|¬H) - 如果假设不成立，观察到该证据的可能性
        
        Returns:
            后验概率 P(H|E)
        """
        if prior <= 0 or prior >= 1:
            return prior
        
        numerator = likelihood_true * prior
        denominator = numerator + likelihood_false * (1 - prior)
        
        if denominator == 0:
            return prior
        
        posterior = numerator / denominator
        return posterior
    
    def chain_update(self, prior: float, 
                    evidence_list: List[Tuple[float, float]]) -> List[float]:
        """
        贝叶斯链式更新
        
        每出现一个证据，概率就更新一次
        
        Args:
            prior: 初始先验概率
            evidence_list: [(like_true, like_false), ...]
                           每个证据的似然度对
        
        Returns:
            概率更新历史 [prior, post1, post2, ...]
        """
        current = prior
        history = [current]
        
        for i, (lt, lf) in enumerate(evidence_list):
            current = self.update(current, lt, lf)
            history.append(current)
        
        return history
    
    def update_from_news(self, prior: float, news_impact: str) -> float:
        """
        根据新闻影响更新概率（简化版）
        
        Args:
            prior: 先验概率
            news_impact: 新闻影响程度 ('very_positive', 'positive', 'neutral', 
                         'negative', 'very_negative')
        
        Returns:
            更新后的概率
        """
        # 预定义的新闻影响似然度
        impact_map = {
            'very_positive': (0.90, 0.10),   # (like_true, like_false)
            'positive': (0.75, 0.25),
            'neutral': (0.50, 0.50),
            'negative': (0.25, 0.75),
            'very_negative': (0.10, 0.90),
        }
        
        if news_impact not in impact_map:
            return prior
        
        lt, lf = impact_map[news_impact]
        return self.update(prior, lt, lf)
    
    def analyze_update(self, prior: float, evidence_list: List[Tuple[float, float]]) -> Dict:
        """
        分析贝叶斯更新过程
        
        Args:
            prior: 初始概率
            evidence_list: 证据列表
        
        Returns:
            分析报告
        """
        history = self.chain_update(prior, evidence_list)
        
        total_change = history[-1] - history[0]
        max_prob = max(history)
        min_prob = min(history)
        volatility = max_prob - min_prob
        
        return {
            'initial': history[0],
            'final': history[-1],
            'total_change': total_change,
            'max': max_prob,
            'min': min_prob,
            'volatility': volatility,
            'steps': len(evidence_list),
            'history': history
        }


def main():
    """测试函数"""
    print("\n" + "="*60)
    print("🔄 贝叶斯更新引擎 - 测试")
    print("="*60)
    
    # 测试场景 1：停火协议
    print("\n📰 场景 1：停火协议概率更新")
    print("-" * 60)
    
    prior = 0.30  # 初始概率 30%
    evidence = [
        (0.80, 0.25),  # 证据 1：双方同意谈判
        (0.70, 0.15),  # 证据 2：卫星图像确认撤军
        (0.90, 0.30),  # 证据 3：官方声明发布
    ]
    
    updater = BayesUpdater()
    history = updater.chain_update(prior, evidence)
    
    print(f"初始概率：{prior:.0%}")
    print()
    
    for i, (new_prob, (lt, lf)) in enumerate(zip(history[1:], evidence), 1):
        change = new_prob - history[i-1]
        print(f"证据{i}后：{new_prob:.0%} (变化：{change:+.0%})")
    
    print(f"\n最终概率：{history[-1]:.0%}")
    print(f"总变化：{history[-1] - history[0]:+.0%}")
    
    # 测试场景 2：新闻影响
    print("\n\n📰 场景 2：新闻影响更新")
    print("-" * 60)
    
    prior = 0.50
    news_sequence = ['positive', 'very_positive', 'neutral', 'negative']
    
    current = prior
    print(f"初始概率：{current:.0%}")
    
    for news in news_sequence:
        new_prob = updater.update_from_news(current, news)
        print(f"新闻：{news:<15} → {new_prob:.0%} (变化：{new_prob-current:+.0%})")
        current = new_prob
    
    print("\n" + "="*60)
    print("💡 提示：贝叶斯更新避免锚定效应和近因效应")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
