#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略 2：动量策略
基于价格突破 + 成交量确认
"""

import pandas as pd
import numpy as np

class MomentumStrategy:
    """动量策略"""
    
    def __init__(self, config):
        self.params = config["parameters"]
    
    def calculate_indicators(self, df):
        """计算技术指标"""
        df = df.copy()
        
        # 价格动量（N 日收益率）
        df["momentum"] = df["close"].pct_change(periods=self.params["lookback_period"])
        
        # 成交量 MA
        df["volume_ma"] = df["volume"].rolling(window=20).mean()
        df["volume_ratio"] = df["volume"] / df["volume_ma"]
        
        # 布林带
        df["BB_mid"] = df["close"].rolling(window=20).mean()
        df["BB_std"] = df["close"].rolling(window=20).std()
        df["BB_upper"] = df["BB_mid"] + 2 * df["BB_std"]
        df["BB_lower"] = df["BB_mid"] - 2 * df["BB_std"]
        
        # 最高价突破
        df["high_20d"] = df["high"].rolling(window=20).max()
        df["low_20d"] = df["low"].rolling(window=20).min()
        
        return df
    
    def generate_signal(self, symbol, market, df):
        """生成交易信号"""
        if len(df) < self.params["lookback_period"] + 20:
            return None
        
        df = self.calculate_indicators(df)
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        signal = {
            "symbol": symbol,
            "market": market,
            "price": latest["close"],
            "timestamp": latest["date"]
        }
        
        # 买入信号：突破 20 日高点 + 成交量放大 + 动量为正
        breakout = latest["close"] > prev["high_20d"]
        volume_confirmed = latest["volume_ratio"] > self.params["volume_threshold"]
        momentum_positive = latest["momentum"] > 0
        
        if breakout and volume_confirmed and momentum_positive:
            signal["action"] = "buy"
            signal["confidence"] = 85
            signal["reason"] = f"突破 20 日高点 + 成交量{latest['volume_ratio']:.1f}倍 + 动量{latest['momentum']*100:.1f}%"
            signal["quantity"] = self.calculate_quantity(latest["close"])
            return signal
        
        # 卖出信号：跌破 20 日低点 或 动量转负
        breakdown = latest["close"] < prev["low_20d"]
        momentum_negative = latest["momentum"] < -self.params["breakout_threshold"]
        
        if breakdown or momentum_negative:
            signal["action"] = "sell"
            signal["confidence"] = 70
            signal["reason"] = "跌破支撑或动量转负"
            signal["quantity"] = self.calculate_quantity(latest["close"])
            return signal
        
        return None
    
    def calculate_quantity(self, price, position_value=1000):
        """计算买入数量"""
        return int(position_value / price)
