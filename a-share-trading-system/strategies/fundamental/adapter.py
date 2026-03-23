#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股统一交易系统 - 基本面策略适配器
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
    运行基本面策略
    
    Returns:
        dict: {"signals": [...], "trades": int, "pnl": float, "details": {...}}
    """
    try:
        signals = []
        
        # 模拟 A 股基本面数据
        mock_stocks = [
            {"code": "600519", "name": "贵州茅台", "pe": 28.5, "roe": 32.5, "revenue_growth": 18.2, "profit_growth": 22.5},
            {"code": "300750", "name": "宁德时代", "pe": 22.3, "roe": 18.5, "revenue_growth": 35.8, "profit_growth": 42.3},
            {"code": "002594", "name": "比亚迪", "pe": 35.2, "roe": 20.1, "revenue_growth": 52.3, "profit_growth": 78.5},
            {"code": "601318", "name": "中国平安", "pe": 8.5, "roe": 15.2, "revenue_growth": 5.8, "profit_growth": 8.2},
            {"code": "000858", "name": "五粮液", "pe": 18.5, "roe": 25.3, "revenue_growth": 15.2, "profit_growth": 18.8},
        ]
        
        for stock in mock_stocks:
            pe = stock.get('pe', 50)
            roe = stock.get('roe', 10)
            revenue_growth = stock.get('revenue_growth', 0)
            profit_growth = stock.get('profit_growth', 0)
            
            # 价值选股（低 PE + 高 ROE）
            if pe < 20 and roe > 15:
                signals.append({
                    "type": "Fundamental",
                    "strategy": "Value",
                    "code": stock['code'],
                    "name": stock['name'],
                    "signal": "BUY",
                    "reason": f"低估值 (PE={pe}, ROE={roe}%)",
                    "metrics": {"pe": pe, "roe": roe}
                })
            
            # 成长选股（高增长）
            if revenue_growth > 30 and profit_growth > 30:
                signals.append({
                    "type": "Fundamental",
                    "strategy": "Growth",
                    "code": stock['code'],
                    "name": stock['name'],
                    "signal": "BUY",
                    "reason": f"高增长 (收入 +{revenue_growth}%, 利润 +{profit_growth}%)",
                    "metrics": {"revenue_growth": revenue_growth, "profit_growth": profit_growth}
                })
        
        return {
            "signals": signals,
            "trades": len(signals),
            "pnl": 0.0,
            "details": {
                "stocks_scanned": len(mock_stocks),
                "value_signals": len([s for s in signals if s['strategy'] == 'Value']),
                "growth_signals": len([s for s in signals if s['strategy'] == 'Growth']),
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
