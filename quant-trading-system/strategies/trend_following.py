#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略 1：趋势跟踪策略
基于 MA 金叉/死叉 + MACD + RSI 过滤
"""

import pandas as pd
import numpy as np

class TrendFollowingStrategy:
    """趋势跟踪策略"""
    
    def __init__(self, config):
        self.params = config["parameters"]
    
    def calculate_indicators(self, df):
        """计算技术指标"""
        df = df.copy()
        
        # MA 均线
        df["MA5"] = df["close"].rolling(window=self.params["ma_short"]).mean()
        df["MA20"] = df["close"].rolling(window=self.params["ma_long"]).mean()
        
        # MACD
        exp1 = df["close"].ewm(span=12, adjust=False).mean()
        exp2 = df["close"].ewm(span=26, adjust=False).mean()
        df["DIF"] = exp1 - exp2
        df["DEA"] = df["DIF"].ewm(span=9, adjust=False).mean()
        df["MACD"] = 2 * (df["DIF"] - df["DEA"])
        
        # RSI
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.params["rsi_period"]).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.params["rsi_period"]).mean()
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))
        
        return df
    
    def generate_signal(self, symbol, market, df):
        """生成交易信号"""
        if len(df) < self.params["ma_long"]:
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
        
        # 买入信号：MA5 上穿 MA20 + MACD 金叉 + RSI<70
        ma_golden_cross = (prev["MA5"] <= prev["MA20"]) and (latest["MA5"] > latest["MA20"])
        macd_golden_cross = (prev["MACD"] <= 0) and (latest["MACD"] > 0)
        rsi_ok = latest["RSI"] < self.params["rsi_overbought"]
        
        if ma_golden_cross and macd_golden_cross and rsi_ok:
            signal["action"] = "buy"
            signal["confidence"] = 80
            signal["reason"] = "MA 金叉 + MACD 金叉 + RSI 未超买"
            signal["quantity"] = self.calculate_quantity(latest["close"])
            return signal
        
        # 卖出信号：MA5 下穿 MA20 + MACD 死叉
        ma_dead_cross = (prev["MA5"] >= prev["MA20"]) and (latest["MA5"] < latest["MA20"])
        macd_dead_cross = (prev["MACD"] >= 0) and (latest["MACD"] < 0)
        
        if ma_dead_cross or macd_dead_cross:
            signal["action"] = "sell"
            signal["confidence"] = 75
            signal["reason"] = "MA 死叉或 MACD 死叉"
            signal["quantity"] = self.calculate_quantity(latest["close"])
            return signal
        
        return None
    
    def calculate_quantity(self, price, position_value=1000):
        """计算买入数量"""
        return int(position_value / price)
