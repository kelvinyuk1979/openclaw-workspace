#!/usr/bin/env python3
"""
Edge 计算器测试
"""

import pytest
from datetime import datetime, timedelta
import sys
sys.path.insert(0, 'src')

from analyzer import EdgeAnalyzer


def test_edge_calculation_basic():
    """测试基础 Edge 计算"""
    config = {
        'trading': {
            'max_capital_per_trade': 12000,
            'position_sizing': {
                'min_position_size': 500,
                'max_position_size': 5000
            }
        }
    }
    
    analyzer = EdgeAnalyzer(config)
    
    signal = {
        'market_name': 'Test Market',
        'true_probability': 0.68,
        'market_price': 0.23,
        'settlement_time': datetime.utcnow() + timedelta(minutes=60),
        'confidence': 0.90
    }
    
    edge_data = analyzer.calculate_edge(signal)
    
    # 验证 Edge 计算
    expected_edge = ((0.68 - 0.23) / 0.23) * 100
    assert abs(edge_data['edge_percent'] - expected_edge) < 0.01
    
    # 验证调整后 Edge
    assert edge_data['adjusted_edge'] == expected_edge * 0.90
    
    # 验证仓位计算
    assert edge_data['required_capital'] >= 500
    assert edge_data['required_capital'] <= 5000
    
    print(f"✅ 基础 Edge 计算测试通过")
    print(f"   Edge: {edge_data['edge_percent']:.2f}%")
    print(f"   调整后 Edge: {edge_data['adjusted_edge']:.2f}%")
    print(f"   仓位：${edge_data['required_capital']:,.2f}")


def test_edge_calculation_low_probability():
    """测试低概率场景"""
    config = {
        'trading': {
            'max_capital_per_trade': 12000,
            'position_sizing': {
                'min_position_size': 500,
                'max_position_size': 5000
            }
        }
    }
    
    analyzer = EdgeAnalyzer(config)
    
    signal = {
        'market_name': 'Low Prob Market',
        'true_probability': 0.30,
        'market_price': 0.15,
        'settlement_time': datetime.utcnow() + timedelta(minutes=90),
        'confidence': 0.75
    }
    
    edge_data = analyzer.calculate_edge(signal)
    
    # Edge = (0.30 - 0.15) / 0.15 = 100%
    assert abs(edge_data['edge_percent'] - 100.0) < 0.01
    
    print(f"✅ 低概率场景测试通过")
    print(f"   Edge: {edge_data['edge_percent']:.2f}%")


def test_edge_calculation_high_confidence():
    """测试高置信度场景"""
    config = {
        'trading': {
            'max_capital_per_trade': 12000,
            'position_sizing': {
                'min_position_size': 500,
                'max_position_size': 5000
            }
        }
    }
    
    analyzer = EdgeAnalyzer(config)
    
    signal = {
        'market_name': 'High Confidence Market',
        'true_probability': 0.95,
        'market_price': 0.50,
        'settlement_time': datetime.utcnow() + timedelta(minutes=30),
        'confidence': 0.95
    }
    
    edge_data = analyzer.calculate_edge(signal)
    
    # Edge = (0.95 - 0.50) / 0.50 = 90%
    assert abs(edge_data['edge_percent'] - 90.0) < 0.01
    
    # 高置信度 + 短时间窗口应该获得较大仓位
    assert edge_data['required_capital'] >= 2000
    
    print(f"✅ 高置信度场景测试通过")
    print(f"   Edge: {edge_data['edge_percent']:.2f}%")
    print(f"   仓位：${edge_data['required_capital']:,.2f}")


def test_portfolio_metrics():
    """测试投资组合指标计算"""
    config = {
        'trading': {
            'max_capital_per_trade': 12000,
            'position_sizing': {
                'min_position_size': 500,
                'max_position_size': 5000
            }
        }
    }
    
    analyzer = EdgeAnalyzer(config)
    
    # 模拟 2026-03-14 的 6 笔交易
    opportunities = [
        {
            'edge': {
                'required_capital': 2000,
                'expected_return': 8200,
                'adjusted_edge': 195.65,
                'settlement_minutes': 75,
                'risk_reward_ratio': 3.1
            }
        },
        {
            'edge': {
                'required_capital': 2000,
                'expected_return': 6900,
                'adjusted_edge': 222.58,
                'settlement_minutes': 90,
                'risk_reward_ratio': 2.45
            }
        },
        {
            'edge': {
                'required_capital': 2000,
                'expected_return': 11400,
                'adjusted_edge': 426.32,
                'settlement_minutes': 120,
                'risk_reward_ratio': 4.7
            }
        }
    ]
    
    metrics = analyzer.calculate_portfolio_metrics(opportunities)
    
    # 验证总资本
    assert metrics['total_capital'] == 6000
    
    # 验证总预期回报
    assert metrics['total_expected_return'] == 26500
    
    # 验证总 ROI
    expected_roi = (26500 / 6000) * 100
    assert abs(metrics['total_roi_percent'] - expected_roi) < 0.01
    
    # 验证分散度
    assert metrics['diversification'] == 3
    
    print(f"✅ 投资组合指标测试通过")
    print(f"   总资本：${metrics['total_capital']:,.0f}")
    print(f"   总预期回报：${metrics['total_expected_return']:,.0f}")
    print(f"   总 ROI: {metrics['total_roi_percent']:.2f}%")
    print(f"   分散度：{metrics['diversification']}")


if __name__ == '__main__':
    print("开始运行 Edge 计算器测试...\n")
    
    test_edge_calculation_basic()
    print()
    
    test_edge_calculation_low_probability()
    print()
    
    test_edge_calculation_high_confidence()
    print()
    
    test_portfolio_metrics()
    print()
    
    print("✅ 所有测试通过！")
