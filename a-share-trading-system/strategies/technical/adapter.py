#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股统一交易系统 - 技术面策略适配器
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 添加原项目路径
ORIGINAL_DIR = Path(__file__).parent.parent.parent / 'quant-trading-system'
sys.path.insert(0, str(ORIGINAL_DIR))


def run(config: dict = None) -> dict:
    """
    运行技术面策略
    
    Returns:
        dict: {"signals": [...], "trades": int, "pnl": float, "details": {...}}
    """
    try:
        signals = []
        
        # 模拟 A 股信号（实际应调用原项目）
        mock_stocks = [
            {"code": "600519", "name": "贵州茅台", "price": 1680.50, "change": 2.3, "rsi": 65, "macd": "bullish"},
            {"code": "300750", "name": "宁德时代", "price": 185.20, "change": -1.5, "rsi": 35, "macd": "bearish"},
            {"code": "002594", "name": "比亚迪", "price": 220.80, "change": 3.8, "rsi": 72, "macd": "bullish"},
            {"code": "00700", "name": "腾讯控股", "price": 380.50, "change": 1.2, "rsi": 55, "macd": "neutral"},
            {"code": "601318", "name": "中国平安", "price": 42.30, "change": -0.8, "rsi": 42, "macd": "bearish"},
        ]
        
        for stock in mock_stocks:
            # RSI 信号
            rsi = stock.get('rsi', 50)
            if rsi < 30:
                signals.append({
                    "type": "Technical",
                    "indicator": "RSI",
                    "code": stock['code'],
                    "name": stock['name'],
                    "signal": "BUY",
                    "reason": f"RSI 超卖 ({rsi})",
                    "price": stock['price'],
                    "change": stock['change']
                })
            elif rsi > 70:
                signals.append({
                    "type": "Technical",
                    "indicator": "RSI",
                    "code": stock['code'],
                    "name": stock['name'],
                    "signal": "SELL",
                    "reason": f"RSI 超买 ({rsi})",
                    "price": stock['price'],
                    "change": stock['change']
                })
            
            # MACD 信号
            macd = stock.get('macd', 'neutral')
            if macd == 'bullish' and rsi < 60:
                signals.append({
                    "type": "Technical",
                    "indicator": "MACD",
                    "code": stock['code'],
                    "name": stock['name'],
                    "signal": "BUY",
                    "reason": "MACD 金叉",
                    "price": stock['price'],
                    "change": stock['change']
                })
            elif macd == 'bearish' and rsi > 40:
                signals.append({
                    "type": "Technical",
                    "indicator": "MACD",
                    "code": stock['code'],
                    "name": stock['name'],
                    "signal": "SELL",
                    "reason": "MACD 死叉",
                    "price": stock['price'],
                    "change": stock['change']
                })
        
        return {
            "signals": signals,
            "trades": len(signals),
            "pnl": 0.0,
            "details": {
                "stocks_scanned": len(mock_stocks),
                "buy_signals": len([s for s in signals if s['signal'] == 'BUY']),
                "sell_signals": len([s for s in signals if s['signal'] == 'SELL']),
                "last_scan": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
    except Exception as e:
        return {
            "signals": [],
            "trades": 0,
            "pnl": 0.0,
            "error": str(e)
        }


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, ensure_ascii=False, indent=2))
