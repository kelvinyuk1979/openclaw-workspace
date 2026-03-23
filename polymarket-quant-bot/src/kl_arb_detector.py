#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KL 散度套利检测器 [FRM-005]
发现相关市场间的定价脱节，执行统计套利
"""

import numpy as np
from itertools import combinations
from typing import Dict, List, Tuple

class KLArbDetector:
    """KL 散度套利检测器"""
    
    def __init__(self, threshold: float = 0.15):
        """
        初始化
        
        Args:
            threshold: KL 散度阈值，默认 0.15
                      超过此值认为存在套利机会
        """
        self.threshold = threshold
    
    def kl_divergence(self, p: List[float], q: List[float]) -> float:
        """
        计算 KL 散度（相对熵）
        
        公式：DKL(P∥Q) = ∑ Pi × ln(Pi/Qi)
        
        Args:
            p: 概率分布 P（市场 A）
            q: 概率分布 Q（市场 B）
        
        Returns:
            KL 散度值
        """
        p = np.array(p, dtype=np.float64)
        q = np.array(q, dtype=np.float64)
        
        # 归一化
        p = p / np.sum(p)
        q = q / np.sum(q)
        
        # 避免除零和对数负数
        p = np.clip(p, 1e-10, 1.0)
        q = np.clip(q, 1e-10, 1.0)
        
        # 重新归一化
        p = p / np.sum(p)
        q = q / np.sum(q)
        
        # 计算 KL 散度
        kl = float(np.sum(p * np.log(p / q)))
        
        return kl
    
    def symmetric_kl(self, p: List[float], q: List[float]) -> float:
        """
        对称 KL 散度
        
        DKL_sym(P,Q) = (DKL(P∥Q) + DKL(Q∥P)) / 2
        
        Args:
            p: 概率分布 P
            q: 概率分布 Q
        
        Returns:
            对称 KL 散度
        """
        kl_pq = self.kl_divergence(p, q)
        kl_qp = self.kl_divergence(q, p)
        
        return (kl_pq + kl_qp) / 2
    
    def scan(self, markets: Dict[str, List[float]]) -> List[Dict]:
        """
        扫描相关市场的 KL 散度
        
        Args:
            markets: {'market_name': [p_yes, p_no], ...}
        
        Returns:
            套利机会列表
        """
        opportunities = []
        
        # 两两比较所有市场
        for (name_a, dist_a), (name_b, dist_b) in combinations(markets.items(), 2):
            kl = self.symmetric_kl(dist_a, dist_b)
            
            is_arb = kl > self.threshold
            
            opportunities.append({
                'market_a': name_a,
                'market_b': name_b,
                'kl_divergence': kl,
                'is_arbitrage': is_arb,
                'signal': 'ARB' if is_arb else 'SKIP'
            })
        
        # 按 KL 散度排序
        opportunities.sort(key=lambda x: x['kl_divergence'], reverse=True)
        
        return opportunities
    
    def detect_correlated_pairs(self, markets: Dict[str, List[float]], 
                                correlation_map: Dict[str, str]) -> List[Dict]:
        """
        检测已知相关市场对之间的 KL 散度
        
        Args:
            markets: 市场数据
            correlation_map: {'market_a': 'market_b', ...} 已知相关对
        
        Returns:
            机会列表
        """
        opportunities = []
        
        for market_a, market_b in correlation_map.items():
            if market_a not in markets or market_b not in markets:
                continue
            
            dist_a = markets[market_a]
            dist_b = markets[market_b]
            
            kl = self.symmetric_kl(dist_a, dist_b)
            
            if kl > self.threshold:
                opportunities.append({
                    'market_a': market_a,
                    'market_b': market_b,
                    'kl_divergence': kl,
                    'signal': 'ARB',
                    'confidence': 'HIGH' if kl > 0.25 else 'MEDIUM'
                })
        
        return opportunities
    
    def calculate_arb_ratio(self, price_a: float, price_b: float) -> Dict:
        """
        计算套利对冲比例
        
        Args:
            price_a: 市场 A 的价格
            price_b: 市场 B 的价格
        
        Returns:
            对冲比例建议
        """
        # 简单对冲：买入低估，卖出高估
        if price_a < price_b:
            long_market = 'A'
            short_market = 'B'
            gap = price_b - price_a
        else:
            long_market = 'B'
            short_market = 'A'
            gap = price_a - price_b
        
        # 对冲比例（简化）
        hedge_ratio = abs(price_a - price_b) / max(price_a, price_b)
        
        return {
            'long_market': long_market,
            'short_market': short_market,
            'price_gap': gap,
            'hedge_ratio': hedge_ratio,
            'market_neutral': True
        }


def main():
    """测试函数"""
    print("\n" + "="*60)
    print("⚡ KL 散度套利检测器 - 测试")
    print("="*60)
    
    detector = KLArbDetector(threshold=0.15)
    
    # 测试数据：相关市场
    test_markets = {
        'X_nom': [0.70, 0.30],  # X 赢得党内提名
        'X_gen': [0.55, 0.45],  # X 赢得大选
        'Y_nom': [0.25, 0.75],  # Y 赢得党内提名
        'Y_gen': [0.20, 0.80],  # Y 赢得大选
    }
    
    print("\n🔍 扫描相关市场...\n")
    print(f"{'市场 A':<20} {'市场 B':<20} {'KL 散度':<12} {'信号':<8}")
    print("-" * 65)
    
    opportunities = detector.scan(test_markets)
    
    arb_count = 0
    for opp in opportunities:
        flag = '⚡ ARB' if opp['is_arbitrage'] else ''
        if opp['is_arbitrage']:
            arb_count += 1
        
        print(f"{opp['market_a']:<20} {opp['market_b']:<20} "
              f"{opp['kl_divergence']:<12.4f} {opp['signal']:<8} {flag}")
    
    print(f"\n✅ 发现 {arb_count} 个套利机会（KL > {detector.threshold:.2f}）")
    
    # 对冲比例计算
    print("\n\n💡 对冲建议示例：")
    print("-" * 60)
    
    arb_example = detector.calculate_arb_ratio(0.70, 0.55)
    print(f"市场 A 价格：0.70")
    print(f"市场 B 价格：0.55")
    print(f"做多市场：{arb_example['long_market']}")
    print(f"做空市场：{arb_example['short_market']}")
    print(f"价格缺口：{arb_example['price_gap']:.0%}")
    print(f"对冲比例：{arb_example['hedge_ratio']:.0%}")
    
    print("\n" + "="*60)
    print("💡 提示：KL 散度捕捉市场间的逻辑断裂")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
