#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略 3：均值回归策略
基于布林带 + RSI 超买超卖
"""

import pandas as pd
import numpy as np

class MeanReversionStrategy:
    """均值回归策略"""
    
    def __init__(self, config):
        self.params = config["parameters"]
    
    def calculate_indicators(self, df):
        """计算技术指标"""
        df = df.copy()
        
        # 布林带
        df["BB_mid"] = df["close"].rolling(window=self.params["bollinger_period"]).mean()
        df["BB_std"] = df["close"].rolling(window=self.params["bollinger_period"]).std()
        df["BB_upper"] = df["BB_mid"] + self.params["bollinger_std"] * df["BB_std"]
        df["BB_lower"] = df["BB_mid"] - self.params["bollinger_std"] * df["BB_std"]
        df["BB_pct"] = (df["close"] - df["BB_lower"]) / (df["BB_upper"] - df["BB_lower"])
        
        # RSI
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))
        
        return df
    
    def generate_signal(self, symbol, market, df):
        """生成交易信号"""
        if len(df) < self.params["bollinger_period"] + 20:
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
        
        # 买入信号：触及布林带下轨 + RSI 超卖
        touch_lower_band = latest["close"] <= latest["BB_lower"]
        rsi_oversold = latest["RSI"] < self.params["rsi_oversold"]
        
        if touch_lower_band or rsi_oversold:
            signal["action"] = "buy"
            signal["confidence"] = 70
            signal["reason"] = f"布林带下轨 + RSI={latest['RSI']:.1f}超卖"
            signal["quantity"] = self.calculate_quantity(latest["close"])
            return signal
        
        # 卖出信号：触及布林带上轨 + RSI 超买
        touch_upper_band = latest["close"] >= latest["BB_upper"]
        rsi_overbought = latest["RSI"] > self.params["rsi_overbought"]
        
        if touch_upper_band or rsi_overbought:
            signal["action"] = "sell"
            signal["confidence"] = 70
            signal["reason"] = f"布林带上轨 + RSI={latest['RSI']:.1f}超买"
            signal["quantity"] = self.calculate_quantity(latest["close"])
            return signal
        
        return None
    
    def calculate_quantity(self, price, position_value=750):
        """计算买入数量"""
        return int(position_value / price)
