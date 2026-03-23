#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略 4：多因子选股策略
基于价值 + 成长 + 质量因子
"""

import pandas as pd
import numpy as np

class MultiFactorStrategy:
    """多因子选股策略"""
    
    def __init__(self, config):
        self.params = config["parameters"]
    
    def calculate_factors(self, symbol):
        """计算因子得分（模拟版本）"""
        # TODO: 实际应从财务数据 API 获取
        np.random.seed(hash(symbol) % 10000)
        
        factors = {
            "value_score": np.random.uniform(0, 100),  # 估值因子（PE 倒数等）
            "growth_score": np.random.uniform(0, 100),  # 成长因子（收入/利润增长）
            "quality_score": np.random.uniform(0, 100),  # 质量因子（ROE/ROIC）
            "momentum_score": np.random.uniform(0, 100)  # 动量因子
        }
        
        # 综合得分
        factors["total_score"] = (
            factors["value_score"] * 0.3 +
            factors["growth_score"] * 0.3 +
            factors["quality_score"] * 0.25 +
            factors["momentum_score"] * 0.15
        )
        
        return factors
    
    def generate_signal(self, symbol, market, df=None):
        """生成交易信号"""
        factors = self.calculate_factors(symbol)
        
        # 筛选条件
        value_ok = factors["value_score"] > 60
        growth_ok = factors["growth_score"] > 60
        quality_ok = factors["quality_score"] > 60
        
        signal = {
            "symbol": symbol,
            "market": market,
            "price": df["close"].iloc[-1] if df is not None else 100,
            "timestamp": pd.Timestamp.now()
        }
        
        # 综合得分>70 且各因子都及格时买入
        if factors["total_score"] > 70 and value_ok and growth_ok and quality_ok:
            signal["action"] = "buy"
            signal["confidence"] = min(factors["total_score"], 90)
            signal["reason"] = f"多因子得分{factors['total_score']:.1f} (价值{factors['value_score']:.0f}/成长{factors['growth_score']:.0f}/质量{factors['quality_score']:.0f})"
            signal["quantity"] = self.calculate_quantity(signal["price"])
            signal["factors"] = factors
            return signal
        
        # 综合得分<40 时卖出
        elif factors["total_score"] < 40:
            signal["action"] = "sell"
            signal["confidence"] = 100 - factors["total_score"]
            signal["reason"] = f"多因子得分低{factors['total_score']:.1f}"
            signal["quantity"] = self.calculate_quantity(signal["price"])
            return signal
        
        return None
    
    def calculate_quantity(self, price, position_value=500):
        """计算买入数量"""
        return int(position_value / price)
