#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股统一交易系统 - 情绪面策略适配器
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
    运行情绪面策略
    
    Returns:
        dict: {"signals": [...], "trades": int, "pnl": float, "details": {...}}
    """
    try:
        signals = []
        
        # 模拟 A 股情绪数据
        mock_stocks = [
            {"code": "600519", "name": "贵州茅台", "news_sentiment": 0.75, "capital_flow": 125000000, "social_score": 85},
            {"code": "300750", "name": "宁德时代", "news_sentiment": 0.45, "capital_flow": -85000000, "social_score": 60},
            {"code": "002594", "name": "比亚迪", "news_sentiment": 0.82, "capital_flow": 230000000, "social_score": 92},
            {"code": "00700", "name": "腾讯控股", "news_sentiment": 0.55, "capital_flow": 45000000, "social_score": 70},
            {"code": "601318", "name": "中国平安", "news_sentiment": 0.35, "capital_flow": -120000000, "social_score": 45},
        ]
        
        for stock in mock_stocks:
            news_sentiment = stock.get('news_sentiment', 0.5)
            capital_flow = stock.get('capital_flow', 0)
            social_score = stock.get('social_score', 50)
            
            # 新闻情绪信号
            if news_sentiment > 0.7:
                signals.append({
                    "type": "Sentiment",
                    "indicator": "News",
                    "code": stock['code'],
                    "name": stock['name'],
                    "signal": "BUY",
                    "reason": f"新闻情绪积极 ({news_sentiment:.2f})",
                    "sentiment": news_sentiment
                })
            elif news_sentiment < 0.3:
                signals.append({
                    "type": "Sentiment",
                    "indicator": "News",
                    "code": stock['code'],
                    "name": stock['name'],
                    "signal": "SELL",
                    "reason": f"新闻情绪消极 ({news_sentiment:.2f})",
                    "sentiment": news_sentiment
                })
            
            # 资金流向信号
            if capital_flow > 100000000:  # > 1 亿
                signals.append({
                    "type": "Sentiment",
                    "indicator": "CapitalFlow",
                    "code": stock['code'],
                    "name": stock['name'],
                    "signal": "BUY",
                    "reason": f"主力资金流入 (+{capital_flow/1000000:.1f}M)",
                    "capital_flow": capital_flow
                })
            elif capital_flow < -100000000:  # < -1 亿
                signals.append({
                    "type": "Sentiment",
                    "indicator": "CapitalFlow",
                    "code": stock['code'],
                    "name": stock['name'],
                    "signal": "SELL",
                    "reason": f"主力资金流出 (-{abs(capital_flow)/1000000:.1f}M)",
                    "capital_flow": capital_flow
                })
        
        return {
            "signals": signals,
            "trades": len(signals),
            "pnl": 0.0,
            "details": {
                "stocks_scanned": len(mock_stocks),
                "positive_sentiment": len([s for s in signals if s['signal'] == 'BUY']),
                "negative_sentiment": len([s for s in signals if s['signal'] == 'SELL']),
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
