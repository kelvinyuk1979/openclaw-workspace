#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回测模块
历史数据回测，优化预测模型权重
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from itertools import product

class Backtester:
    """回测引擎"""
    
    def __init__(self, initial_capital: float = 10000):
        """
        初始化
        
        Args:
            initial_capital: 初始资金
        """
        self.initial_capital = initial_capital
        self.results = []
    
    def run(self, historical_data: List[Dict], 
            weights: Dict[str, float],
            strategy: str = 'ev') -> Dict:
        """
        运行回测
        
        Args:
            historical_data: 历史数据列表
                每个元素包含：
                - date: 日期
                - market_id: 市场 ID
                - category: 分类
                - yes_price: 价格
                - volume_24h: 交易量
                - open_interest: 未平仓
                - outcome: 最终结果（1=Yes 赢，0=No 赢）
            weights: 预测模型权重
            strategy: 策略类型 ('ev', 'base_rate', 'kl_arb')
        
        Returns:
            回测结果
        """
        capital = self.initial_capital
        trades = []
        daily_pnl = []
        
        # 按日期分组
        dates = sorted(set(d['date'] for d in historical_data))
        
        for date in dates:
            day_data = [d for d in historical_data if d['date'] == date]
            day_trades = []
            
            for market in day_data:
                # 计算预测概率
                pred_prob = self._predict(market, weights)
                market_price = market['yes_price']
                
                # 计算 EV
                ev = (pred_prob - market_price) / market_price if market_price > 0 else 0
                
                # 交易信号
                if strategy == 'ev':
                    signal = 'BUY' if ev > 0.05 else 'SELL' if ev < -0.05 else 'SKIP'
                elif strategy == 'base_rate':
                    signal = 'BUY' if pred_prob > market_price + 0.05 else 'SKIP'
                else:
                    signal = 'SKIP'
                
                if signal == 'SKIP':
                    continue
                
                # 凯利公式计算仓位
                odds = (1 - market_price) / market_price if market_price > 0 else 0
                kelly = (pred_prob * odds - (1 - pred_prob)) / odds
                kelly = max(kelly * 0.25, 0)  # 1/4 凯利
                kelly = min(kelly, 0.10)  # 最大 10% 仓位
                
                bet_size = capital * kelly
                
                # 计算盈亏
                outcome = market['outcome']
                
                if signal == 'BUY':
                    # 买 Yes
                    if outcome == 1:
                        pnl = bet_size * (1 - market_price) / market_price
                    else:
                        pnl = -bet_size
                else:
                    # 买 No
                    if outcome == 0:
                        pnl = bet_size * market_price / (1 - market_price)
                    else:
                        pnl = -bet_size
                
                capital += pnl
                
                day_trades.append({
                    'date': date,
                    'market_id': market['market_id'],
                    'signal': signal,
                    'bet_size': bet_size,
                    'pnl': pnl,
                    'outcome': outcome
                })
            
            trades.extend(day_trades)
            daily_pnl.append({
                'date': date,
                'pnl': sum(t['pnl'] for t in day_trades),
                'capital': capital,
                'trades': len(day_trades)
            })
        
        # 计算绩效指标
        metrics = self._calculate_metrics(trades, daily_pnl)
        
        return {
            'final_capital': capital,
            'total_return': (capital - self.initial_capital) / self.initial_capital,
            'total_trades': len(trades),
            'winning_trades': sum(1 for t in trades if t['pnl'] > 0),
            'losing_trades': sum(1 for t in trades if t['pnl'] < 0),
            'win_rate': sum(1 for t in trades if t['pnl'] > 0) / max(len(trades), 1),
            'metrics': metrics,
            'daily_pnl': daily_pnl,
            'trades': trades
        }
    
    def _predict(self, market: Dict, weights: Dict[str, float]) -> float:
        """简化版预测"""
        # 基础率
        base_rate = 0.50
        category = market.get('category', '')
        
        if category == 'economics':
            base_rate = 0.60
        elif category == 'crypto':
            base_rate = 0.55
        elif category == 'politics':
            base_rate = 0.52
        
        # 市场情绪
        sentiment = market['yes_price']
        
        # 动量（简化）
        momentum = 0.50
        
        # 交易量
        volume_signal = market['yes_price']
        
        # 新闻
        news_catalyst = 0.55
        
        # 加权平均
        pred_prob = (
            base_rate * weights.get('base_rate', 0.30) +
            sentiment * weights.get('market_sentiment', 0.20) +
            momentum * weights.get('momentum', 0.15) +
            volume_signal * weights.get('volume_signal', 0.15) +
            news_catalyst * weights.get('news_catalyst', 0.20)
        )
        
        return max(0.0, min(1.0, pred_prob))
    
    def _calculate_metrics(self, trades: List[Dict], daily_pnl: List[Dict]) -> Dict:
        """计算绩效指标"""
        if not trades:
            return {}
        
        pnls = [t['pnl'] for t in trades]
        daily_returns = [d['pnl'] / self.initial_capital for d in daily_pnl]
        
        # 夏普比率
        if len(daily_returns) > 1:
            avg_return = np.mean(daily_returns)
            std_return = np.std(daily_returns)
            sharpe = (avg_return / std_return) * np.sqrt(252) if std_return > 0 else 0
        else:
            sharpe = 0
        
        # 最大回撤
        capitals = [d['capital'] for d in daily_pnl]
        peak = capitals[0]
        max_drawdown = 0
        
        for cap in capitals:
            if cap > peak:
                peak = cap
            drawdown = (peak - cap) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return {
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'avg_pnl': np.mean(pnls),
            'std_pnl': np.std(pnls),
            'profit_factor': sum(p for p in pnls if p > 0) / abs(sum(p for p in pnls if p < 0)) if sum(p for p in pnls if p < 0) != 0 else 0,
            'total_pnl': sum(pnls)
        }
    
    def optimize_weights(self, historical_data: List[Dict], 
                        steps: int = 5) -> Tuple[Dict, Dict]:
        """
        优化权重
        
        Args:
            historical_data: 历史数据
            steps: 网格搜索步数
        
        Returns:
            (最佳权重，最佳结果)
        """
        best_weights = None
        best_result = None
        best_sharpe = -999
        
        # 生成权重组合
        weight_range = np.linspace(0.1, 0.5, steps)
        
        print(f"\n🔍 开始网格搜索（{steps}^5 = {steps**5} 种组合）...\n")
        
        count = 0
        for w1, w2, w3, w4, w5 in product(weight_range, repeat=5):
            # 归一化
            total = w1 + w2 + w3 + w4 + w5
            weights = {
                'base_rate': w1 / total,
                'market_sentiment': w2 / total,
                'momentum': w3 / total,
                'volume_signal': w4 / total,
                'news_catalyst': w5 / total,
            }
            
            # 运行回测
            result = self.run(historical_data, weights)
            sharpe = result['metrics'].get('sharpe_ratio', 0)
            
            count += 1
            
            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_weights = weights
                best_result = result
                
                print(f"  [{count}/{steps**5}] 新记录：Sharpe={sharpe:.2f}, "
                      f"回报={result['total_return']:.1%}")
        
        return best_weights, best_result


def generate_mock_data(days: int = 100) -> List[Dict]:
    """生成模拟历史数据"""
    np.random.seed(42)
    
    markets = [
        {'market_id': 'fed-cut', 'category': 'economics', 'base_prob': 0.55},
        {'market_id': 'btc-100k', 'category': 'crypto', 'base_prob': 0.60},
        {'market_id': 'trump-oh', 'category': 'politics', 'base_prob': 0.48},
        {'market_id': 'ceasefire', 'category': 'geopolitics', 'base_prob': 0.40},
    ]
    
    data = []
    base_date = datetime.now() - timedelta(days=days)
    
    for day in range(days):
        date = (base_date + timedelta(days=day)).strftime('%Y-%m-%d')
        
        for m in markets:
            # 随机价格波动
            yes_price = m['base_prob'] + np.random.normal(0, 0.05)
            yes_price = max(0.1, min(0.9, yes_price))
            
            # 随机结果（基于基础概率）
            outcome = 1 if np.random.random() < m['base_prob'] else 0
            
            data.append({
                'date': date,
                'market_id': m['market_id'],
                'category': m['category'],
                'yes_price': yes_price,
                'volume_24h': np.random.uniform(50000, 500000),
                'open_interest': np.random.uniform(200000, 1000000),
                'outcome': outcome
            })
    
    return data


def main():
    """测试函数"""
    print("\n" + "="*60)
    print("📈 回测系统 - 测试")
    print("="*60)
    
    # 生成模拟数据
    print("\n📊 生成模拟历史数据...")
    data = generate_mock_data(days=100)
    print(f"✅ 生成 {len(data)} 条记录")
    
    # 测试回测
    print("\n🔍 运行回测（默认权重）...")
    backtester = Backtester(initial_capital=10000)
    
    default_weights = {
        'base_rate': 0.30,
        'market_sentiment': 0.20,
        'momentum': 0.15,
        'volume_signal': 0.15,
        'news_catalyst': 0.20,
    }
    
    result = backtester.run(data, default_weights)
    
    print("\n" + "="*60)
    print("📊 回测结果（默认权重）")
    print("="*60)
    print(f"初始资金：${backtester.initial_capital:,.0f}")
    print(f"最终资金：${result['final_capital']:,.0f}")
    print(f"总回报：{result['total_return']:+.1%}")
    print(f"总交易：{result['total_trades']} 笔")
    print(f"胜率：{result['win_rate']:.1%}")
    print(f"夏普比率：{result['metrics'].get('sharpe_ratio', 0):.2f}")
    print(f"最大回撤：{result['metrics'].get('max_drawdown', 0):.1%}")
    print(f"盈亏比：{result['metrics'].get('profit_factor', 0):.2f}")
    
    # 优化权重（小步长测试）
    print("\n\n🔍 优化权重（简化版）...")
    best_weights, best_result = backtester.optimize_weights(data, steps=3)
    
    print("\n" + "="*60)
    print("🏆 最佳权重")
    print("="*60)
    
    if best_weights:
        for k, v in best_weights.items():
            print(f"  {k:<20}: {v:.1%}")
        
        print(f"\n优化后 Sharpe: {best_result['metrics'].get('sharpe_ratio', 0):.2f}")
        print(f"优化后回报：{best_result['total_return']:+.1%}")
    
    print("\n" + "="*60)
    print("💡 提示：实际使用需要更多历史数据")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
