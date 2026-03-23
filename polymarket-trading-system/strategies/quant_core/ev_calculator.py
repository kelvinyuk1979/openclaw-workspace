#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EV 期望值计算器 [FRM-001]
计算市场定价与模型概率的差异，生成交易信号
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class EVCalculator:
    """期望值计算器"""
    
    def __init__(self, threshold: float = 0.05):
        """
        初始化
        
        Args:
            threshold: EV 阈值，默认 0.05（5%）
        """
        self.threshold = threshold
    
    def calculate(self, market_price: float, model_prob: float) -> float:
        """
        计算期望值
        
        公式：EV = (model_prob - market_price) × (1 / market_price)
        
        Args:
            market_price: 市场价格（0-1）
            model_prob: 模型测算的真实概率（0-1）
        
        Returns:
            期望值 EV
        """
        if market_price <= 0 or market_price >= 1:
            return 0.0
        
        ev = (model_prob - market_price) / market_price
        return ev
    
    def signal(self, ev: float) -> str:
        """
        根据 EV 生成交易信号
        
        Args:
            ev: 期望值
        
        Returns:
            'BUY' | 'SELL' | 'SKIP'
        """
        if ev > self.threshold:
            return 'BUY'
        elif ev < -self.threshold:
            return 'SELL'
        else:
            return 'SKIP'
    
    def scan(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        扫描多个市场的 EV 机会
        
        Args:
            df: 包含 market_price 和 model_p 列的 DataFrame
        
        Returns:
            添加 ev 和 signal 列的 DataFrame
        """
        df = df.copy()
        df['ev'] = self.calculate(df['market_price'], df['model_p'])
        df['signal'] = df['ev'].apply(self.signal)
        
        # 按 EV 排序
        opportunities = df[df['signal'] != 'SKIP'].sort_values('ev', ascending=False)
        
        return opportunities
    
    def scan_dict(self, markets: List[Dict]) -> List[Dict]:
        """
        扫描字典格式的市场数据
        
        Args:
            markets: [{'market': str, 'market_price': float, 'model_p': float}, ...]
        
        Returns:
            机会列表
        """
        opportunities = []
        
        for m in markets:
            ev = self.calculate(m['market_price'], m['model_p'])
            signal = self.signal(ev)
            
            if signal != 'SKIP':
                opportunities.append({
                    **m,
                    'ev': ev,
                    'signal': signal
                })
        
        # 按 EV 排序
        opportunities.sort(key=lambda x: x['ev'], reverse=True)
        
        return opportunities


def main():
    """测试函数"""
    print("\n" + "="*60)
    print("📊 EV 期望值计算器 - 测试")
    print("="*60)
    
    # 测试数据
    test_markets = [
        {'market': 'Fed cut Jun', 'market_price': 0.40, 'model_p': 0.55},
        {'market': 'Trump OH', 'market_price': 0.52, 'model_p': 0.42},
        {'market': 'Ceasefire 2024', 'market_price': 0.30, 'model_p': 0.58},
        {'market': 'BTC 100K', 'market_price': 0.65, 'model_p': 0.70},
    ]
    
    calculator = EVCalculator(threshold=0.05)
    
    print("\n🔍 扫描市场...")
    print(f"EV 阈值：{calculator.threshold:.0%}\n")
    
    opportunities = calculator.scan_dict(test_markets)
    
    if opportunities:
        print(f"✅ 发现 {len(opportunities)} 个交易机会：\n")
        
        for opp in opportunities:
            print(f"市场：{opp['market']}")
            print(f"  市场价格：{opp['market_price']:.0%}")
            print(f"  模型概率：{opp['model_p']:.0%}")
            print(f"  EV: {opp['ev']:.2%}")
            print(f"  信号：{opp['signal']}")
            print()
    else:
        print("⚠️  无交易机会（所有市场 EV < 阈值）")
    
    print("="*60)


if __name__ == "__main__":
    main()
